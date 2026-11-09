"""Coverage should distinguish saved data, pending evidence and unsupported links."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from probe import weight_review as review
from probe.weights import asset_signature
from probe import weights


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.runs = self.root / "runs"
        self.runs.mkdir()
        self.add_card("test", '''[[assets]]
key = "weights"
provider = "url"
url = "https://example.org/weights.pt"
[[assets]]
key = "onnx"
provider = "url"
url = "https://example.org/weights.onnx"
''')
        self.add_card("empty", "")

    def add_card(self, model, assets):
        path = self.root / "content/models" / model / "index.md"
        path.parent.mkdir(parents=True)
        path.write_text('+++\ntitle = "Test"\n' + assets + '+++\nCard body.\n')
        return path

    def run_coverage(self, *extra):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = review.main(["coverage", "--repo", str(self.root), "--run-root", str(self.runs), *extra])
        self.assertEqual(code, 0)
        return out.getvalue()

    def report(self, version=review.VERSION):
        asset = review.catalogue(self.root, ["test"])[("test", "weights")]
        record = {"model": "test", "asset": "weights", "status": "ok",
                  "inspection_version": version, "asset_signature": asset_signature(asset),
                  "source_url": asset["url"], "sha256": "a" * 64,
                  "method": "pickle_tensor_metadata",
                  "candidates": [{"container": "root", "tensor_elements": 0, "kind": "tensor_elements"}]}
        folder = self.runs / "one"
        folder.mkdir()
        path = folder / "report.json"
        path.write_text(json.dumps({"schema_version": 1, "created_at": "2026-10-13T12:00:00+00:00", "results": [record]}))
        return path

    def test_summary_excludes_missing_asset_placeholders_and_details_are_opt_in(self):
        text = self.run_coverage()
        self.assertIn("2 models, 1 directly inspectable PyTorch assets", text)
        self.assertIn("1 other assets; 1 models have no directly inspectable asset", text)
        self.assertNotIn("test/onnx", text)
        self.assertNotIn("/None", text)
        detail = self.run_coverage("--details")
        self.assertIn("test/onnx", detail)
        self.assertIn("empty (no assets)", detail)

    def test_pending_evidence_is_not_saved_and_output_stays_read_only(self):
        self.report()
        path = self.root / "content/models/test/index.md"
        before = path.read_bytes()
        output = self.root / "coverage.json"
        text = self.run_coverage("--output", str(output))
        self.assertIn("0/1 assets have current saved counts", text)
        self.assertIn("1/1 assets have usable inspection results", text)
        self.assertIn("review-pending-weights --guide", text)
        rows = json.loads(output.read_text())["results"]
        row = next(r for r in rows if r["asset"] == "weights")
        self.assertEqual(review.coverage_state(row), "Review")
        self.assertEqual(row["proposals"][0]["weight_count"]["value"], 0)
        self.assertEqual(path.read_bytes(), before)

    def test_old_evidence_requires_refresh_and_explicit_report_context_is_preserved(self):
        report = self.report(version="old")
        text = self.run_coverage("--report", str(report), "--model", "test")
        self.assertIn("0/1 assets have usable inspection results", text)
        rows = review.audit(review.catalogue(self.root, ["test"]), review.read_reports([report]))
        self.assertEqual(review.coverage_state(rows[0]), "Refresh")
        # Inspect suggestions must target the selected checkout.
        self.assertIn("--repo " + str(self.root), text)

    def test_replacement_is_not_hidden_by_saved_count_and_unchanged_is_saved(self):
        row = {"stored_status": "current", "status": "pending", "proposals": [{"action": "REPLACE"}]}
        self.assertEqual(review.coverage_state(row), "Review")
        row["proposals"][0]["action"] = "UNCHANGED"
        self.assertEqual(review.coverage_state(row), "Saved")
        row.update(stored_status="missing", proposals=[], status="failed")
        self.assertEqual(review.coverage_state(row), "Blocked")

    def test_no_eligible_assets_is_not_a_failure(self):
        text = self.run_coverage("--model", "empty")
        self.assertIn("1 models, 0 directly inspectable", text)
        self.assertIn("Add a direct PyTorch weight link", text)
        self.assertNotIn("Inspect one asset", text)

    def run_review_guide(self, answers, *extra):
        output = io.StringIO()
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', side_effect=answers), contextlib.redirect_stdout(output):
            code = review.main(['pending', '--guide', '--repo', str(self.root), '--run-root', str(self.runs), *extra])
        self.assertEqual(code, 0)
        return output.getvalue()

    def test_review_guide_cancel_then_accept_preserves_body_and_other_assets(self):
        self.report()
        path = self.root / 'content/models/test/index.md'
        before = path.read_bytes()
        text = self.run_review_guide(['oops', '1', '1', '1', 'n', 'n'])
        self.assertIn('Enter a number', text)
        self.assertIn('ADD test/weights', text)
        self.assertNotIn('empty (no assets)', text)
        self.assertEqual(path.read_bytes(), before)
        self.run_review_guide(['1', '1', '1', 'y', 'n'])
        assets = review.catalogue(self.root, ['test'])
        self.assertEqual(assets[('test', 'weights')]['weight_count']['value'], 0)
        self.assertNotIn('weight_count', assets[('test', 'onnx')])
        self.assertTrue(path.read_text().endswith('+++\nCard body.\n'))

    def test_review_guide_requires_explicit_container_and_handles_eof(self):
        path = self.report()
        report = json.loads(path.read_text())
        report['results'][0]['candidates'].append({'container': 'model', 'kind': 'stored_parameters', 'tensor_elements': 20})
        path.write_text(json.dumps(report))
        card = self.root / 'content/models/test/index.md'
        before = card.read_bytes()
        self.run_review_guide(['1', '1', EOFError()])
        self.assertEqual(card.read_bytes(), before)
        self.run_review_guide(['1', '1', '2', 'y', 'n'])
        count = review.catalogue(self.root, ['test'])[('test', 'weights')]['weight_count']
        self.assertEqual((count['value'], count['container']), (20, 'model'))

    def test_review_guide_empty_or_stale_reports_never_offer_edits(self):
        self.report(version='old')
        text = self.run_review_guide([])
        self.assertIn('No usable pending count changes', text)

    def test_guides_reject_noninteractive_input(self):
        with patch('sys.stdin.isatty', return_value=False), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(review.main(['pending', '--guide', '--repo', str(self.root)]), 1)
            with self.assertRaises(SystemExit):
                weights.main(['--guide', '--repo', str(self.root)])

    def test_inspection_guide_only_downloads_after_confirmation(self):
        args = ['--guide', '--repo', str(self.root), '--run-root', str(self.runs)]
        with patch('sys.stdin.isatty', return_value=True), patch.object(weights, 'inspect_asset') as inspect, contextlib.redirect_stdout(io.StringIO()):
            for answers in (['q'], ['1', '1', 'n'], ['1', EOFError()]):
                with patch('builtins.input', side_effect=answers):
                    self.assertEqual(weights.main(args), 0)
                inspect.assert_not_called()
            inspect.return_value = {'model': 'test', 'asset': 'weights', 'status': 'ok', 'eligible': True, 'candidates': []}
            with patch('builtins.input', side_effect=['1', '1', 'y']):
                self.assertEqual(weights.main(args), 0)
            inspect.assert_called_once()
            self.assertEqual(inspect.call_args.args[0]['asset']['key'], 'weights')
        self.assertEqual(len(list(self.runs.glob('*/report.json'))), 1)

    def test_inspection_guide_all_is_explicit_and_excludes_other_formats(self):
        path = self.root / 'content/models/test/index.md'
        path.write_text(path.read_text().replace('+++\nCard body.',
            '[[assets]]\nkey = "second"\nurl = "https://example.org/second.pth"\n+++\nCard body.'))
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input', side_effect=['1', '3', 'y']), \
                patch.object(weights, 'inspect_asset') as inspect, contextlib.redirect_stdout(io.StringIO()):
            inspect.side_effect = lambda item, *args: dict(model=item['model'], asset=item['asset']['key'], status='ok', candidates=[])
            self.assertEqual(weights.main(['--guide', '--repo', str(self.root), '--run-root', str(self.runs)]), 0)
        self.assertEqual([call.args[0]['asset']['key'] for call in inspect.call_args_list], ['weights', 'second'])

    def test_inspection_filter_hides_pending_assets_but_show_all_restores_them(self):
        self.report()
        args = ['--guide', '--repo', str(self.root), '--run-root', str(self.runs)]
        with patch('sys.stdin.isatty', return_value=True), patch('builtins.input') as prompt, \
                patch.object(weights, 'inspect_asset') as inspect, contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(weights.main(args), 0)
            prompt.assert_not_called()
            inspect.assert_not_called()
            self.assertIn('No PyTorch assets need inspection', output.getvalue())
            prompt.side_effect = ['1', '1', 'n']
            self.assertEqual(weights.main(args + ['--show-all']), 0)
            self.assertIn('weights [Review]', output.getvalue())
            inspect.assert_not_called()

    def test_review_filter_hides_saved_counts_but_show_all_displays_without_edit(self):
        self.report()
        self.run_review_guide(['1', '1', '1', 'y', 'n'])
        path = self.root / 'content/models/test/index.md'
        before = path.read_bytes()
        self.assertIn('No usable pending count changes', self.run_review_guide([]))
        output = self.run_review_guide(['1', '1', '1', 'n'], '--show-all')
        self.assertIn('already matches the model card', output)
        self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
