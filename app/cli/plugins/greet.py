"""
Greet Command Plugin
====================
"""

from colorama import Fore
from app.cli.commands import command


@command("greet", "Display a greeting.", "greet")
def greet_command(*args, **kwargs) -> str:
    """Displays a simple greeting message."""
    msg = "Hello! Welcome to the calculator."
    print(f"{Fore.MAGENTA}{msg}")
    return msg
