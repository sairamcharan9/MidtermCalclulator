"""
Command Loader
==============

Provides a singleton instance of the CommandManager.
"""

from app.cli.commands import CommandManager

command_manager = CommandManager()
