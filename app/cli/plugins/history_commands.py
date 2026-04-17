"""
History-Related Command Plugins
===============================

Provides commands for managing the calculator's history:
history, clear, undo, redo, save, load.
"""

from colorama import Fore
from app.cli.commands import command


@command("history", "Show calculation history.", "history")
def history_command(calculator) -> str:
    """Displays the formatted calculation history."""
    rows = calculator.history.get_all()
    if not rows:
        msg = "No calculations in history."
        print(f"{Fore.YELLOW}{msg}")
        return msg

    lines = ["=== Calculation History ==="]
    for i, row in enumerate(rows, start=1):
        lines.append(f"  {i}. {row['operand_a']} {row['operation']} {row['operand_b']} = {row['result']}")
    lines.append(f"\nTotal: {len(rows)} calculation(s)")
    history_text = "\n".join(lines)
    print(f"{Fore.BLUE}{history_text}")
    return history_text


@command("clear", "Clear the history.", "clear")
def clear_command(calculator) -> str:
    """Clears the calculation history, with undo support."""
    if len(calculator.history) == 0:
        msg = "History is already empty."
        print(f"{Fore.YELLOW}{msg}")
        return msg

    calculator.caretaker.save()
    calculator.history.clear()
    msg = "History cleared."
    calculator._log.info("History cleared.")
    print(f"{Fore.GREEN}{msg}")
    return msg


@command("undo", "Undo the last action.", "undo")
def undo_command(calculator) -> str:
    """Undoes the last action by restoring the previous history state."""
    if calculator.caretaker.undo():
        msg = f"Undo successful. History now contains {len(calculator.history)} calculation(s)."
        calculator._log.info("Undo successful. History size: %d", len(calculator.history))
        print(f"{Fore.GREEN}{msg}")
    else:
        msg = "Nothing to undo."
        calculator._log.info("Undo requested, but undo stack is empty.")
        print(f"{Fore.YELLOW}{msg}")
    return msg


@command("redo", "Redo the last undone action.", "redo")
def redo_command(calculator) -> str:
    """Redoes the last undone action by restoring the next history state."""
    if calculator.caretaker.redo():
        msg = f"Redo successful. History now contains {len(calculator.history)} calculation(s)."
        calculator._log.info("Redo successful. History size: %d", len(calculator.history))
        print(f"{Fore.GREEN}{msg}")
    else:
        msg = "Nothing to redo."
        calculator._log.info("Redo requested, but redo stack is empty.")
        print(f"{Fore.YELLOW}{msg}")
    return msg


@command("save", "Manually save history.", "save")
def save_command(calculator) -> str:
    """Manually saves the current calculation history to a CSV file."""
    path = calculator.history.save_to_csv()
    msg = f"History saved to '{path}'."
    calculator._log.info("History manually saved to %s (%d rows)", path, len(calculator.history))
    print(f"{Fore.GREEN}{msg}")
    return msg


@command("load", "Manually load history.", "load")
def load_command(calculator) -> str:
    """Manually loads calculation history from a CSV file."""
    count = calculator.history.load_from_csv()
    msg = f"Loaded {count} calculation(s) from '{calculator.history.csv_path}'."
    calculator._log.info(
        "History loaded from %s, containing %d rows", calculator.history.csv_path, count
    )
    print(f"{Fore.GREEN}{msg}")
    return msg
