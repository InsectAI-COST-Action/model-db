(function () {
  "use strict";

  var form = document.getElementById("filter-bar");
  if (!form) { return; }

  var rows = [].slice.call(document.querySelectorAll("tr[data-id]"));
  if (!rows.length) { return; }

  var searchInput = document.getElementById("filter-q");
  var counter = document.getElementById("result-count");

  /* The facets are whatever the build emitted as checkboxes, so adding one to
     filter-bar.html cannot silently fail to be filtered here. */
  var boxes = [].slice.call(form.querySelectorAll("input[data-facet]"));
  var NAMES = [];
  boxes.forEach(function (box) {
    var name = box.getAttribute("data-facet");
    if (NAMES.indexOf(name) === -1) { NAMES.push(name); }
  });

  var LISTS = (form.getAttribute("data-list-facets") || "").split(" ");

  function checkedFacets() {
    var state = {};
    NAMES.forEach(function (name) { state[name] = []; });
    boxes.forEach(function (box) {
      if (box.checked) { state[box.getAttribute("data-facet")].push(box.value); }
    });
    return state;
  }

  function readUrl() {
    var params = new URLSearchParams(location.search);
    if (searchInput && params.get("q")) { searchInput.value = params.get("q"); }
    boxes.forEach(function (box) {
      if (params.getAll(box.getAttribute("data-facet")).indexOf(box.value) !== -1) {
        box.checked = true;
      }
    });
  }

  function writeUrl(query, facets) {
    var params = new URLSearchParams();
    if (query) { params.set("q", query); }
    NAMES.forEach(function (name) {
      facets[name].forEach(function (value) { params.append(name, value); });
    });
    var qs = params.toString();
    history.replaceState(null, "", location.pathname + (qs ? "?" + qs : ""));
  }

  function matches(row, query, facets) {
    for (var i = 0; i < NAMES.length; i++) {
      var name = NAMES[i];
      var wanted = facets[name];
      if (!wanted.length) { continue; }
      var actual = row.getAttribute("data-" + name) || "";
      var values = LISTS.indexOf(name) !== -1 ? actual.split(";") : [actual];
      if (!wanted.some(function (v) { return values.indexOf(v) !== -1; })) {
        return false;
      }
    }
    if (!query) { return true; }
    return (row.getAttribute("data-search") || "").indexOf(query) !== -1;
  }

  function apply() {
    var query = searchInput ? searchInput.value.trim().toLowerCase() : "";
    var facets = checkedFacets();
    var visible = 0;

    rows.forEach(function (row) {
      var show = matches(row, query, facets);
      if (show) { visible++; }
      if (show === row.hasAttribute("hidden")) { row.toggleAttribute("hidden", !show); }
    });

    if (counter) {
      var filtering = Boolean(query) || NAMES.some(function (n) { return facets[n].length; });
      counter.textContent = filtering ? visible + " of " + rows.length + " models match." : "";
    }

    writeUrl(query, facets);
  }

  var timer = null;
  function debouncedApply() {
    clearTimeout(timer);
    timer = setTimeout(apply, 120);
  }

  if (searchInput) {
    searchInput.addEventListener("input", debouncedApply);
    searchInput.addEventListener("keydown", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        clearTimeout(timer);
        apply();
      }
    });
  }

  form.addEventListener("submit", function (event) { event.preventDefault(); });
  form.addEventListener("change", function (event) {
    if (event.target && event.target.hasAttribute("data-facet")) { apply(); }
  });

  var reset = document.getElementById("filter-reset");
  if (reset) {
    reset.addEventListener("click", function (event) {
      event.preventDefault();
      if (searchInput) { searchInput.value = ""; }
      boxes.forEach(function (box) { box.checked = false; });
      apply();
    });
  }

  readUrl();
  if (location.search) { apply(); }
})();
