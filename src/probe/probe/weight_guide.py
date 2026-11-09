"""Small numbered menus shared by the weight inspection and review commands."""
import sys


class Cancelled(Exception):
    pass


def require_terminal():
    if not sys.stdin.isatty():
        raise ValueError("--guide requires an interactive terminal; use explicit CLI selectors in scripts")


def choose(title, labels):
    print("\n" + title)
    for number, label in enumerate(labels, 1):
        print(f"  {number}. {label}")
    print("  q. Cancel")
    while True:
        answer = input("Choose a number (Enter to cancel): ").strip()
        if not answer or answer.lower() == "q":
            raise Cancelled()
        if answer.isdecimal() and 1 <= int(answer) <= len(labels):
            return int(answer) - 1
        print(f"Enter a number from 1 to {len(labels)}, or q to cancel.")


def confirm(prompt):
    return input(prompt + " [y/N] ").strip().lower() == "y"
