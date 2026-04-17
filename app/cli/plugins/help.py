"""
Help Command Plugin
===================

Provides the 'help' command, which dynamically generates a help message
based on all registered commands in the CommandManager.
"""
from colorama import Fore
from app.cli.command_loader import command_manager
from app.cli.commands import command


@command("help", "Show this help message.", "help or ?")
def help_command(*args, **kwargs) -> str:
    """
    Dynamically generates and displays a help message.
    """
    commands = command_manager.get_all_commands()

    arithmetic_cmds = [cmd for cmd in commands if "<" in cmd.usage]
    special_cmds = [cmd for cmd in commands if "<" not in cmd.usage]

    help_text = "=== Calculator Help ===\n\n"

    if arithmetic_cmds:
        help_text += "Available Operations:\n"
        for cmd in arithmetic_cmds:
            help_text += f"  {cmd.usage:<20} - {cmd.description}\n"
        help_text += "\n"

    if special_cmds:
        help_text += "Special Commands:\n"
        for cmd in special_cmds:
            help_text += f"  {cmd.usage:<20} - {cmd.description}\n"

    help_text += "\nExample Usage:\n  add 10 5\n  history\n  exit"

    print(f"{Fore.CYAN}{help_text}")
    return help_text


# Register '?' as an alias for 'help'
command_manager.register("?", help_command, "Alias for help.", "?")
