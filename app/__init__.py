"""
Application Package Initialization
===================================

Initializes the application package and dynamically loads all plugins from
`app/cli/plugins/`. Dynamic loading ensures that commands registered with
the `@command` decorator are recognized by the `CommandManager` at startup.

Adding new functionality only requires creating a new Python file in
`app/cli/plugins/` — no core changes needed.
"""

import os
import importlib
import sys
import logging

from app.core.logger import get_logger

_log: logging.Logger = get_logger(__name__)


def load_plugins() -> None:
    """
    Dynamically discovers and loads all plugins from `app/cli/plugins/`.

    Also loads arithmetic operations from `app.cli.operations` so that all
    built-in arithmetic commands are registered before the REPL starts.
    """
    # Load arithmetic operations first (registers add/subtract/multiply/etc.)
    ops_module = "app.cli.operations"
    try:
        if ops_module in sys.modules:
            importlib.reload(sys.modules[ops_module])
        else:
            importlib.import_module(ops_module)
        _log.info("Successfully loaded arithmetic operations.")
    except ImportError as e:
        _log.error("Failed to load arithmetic operations: %s", e)

    # Discover and load all plugin files from app/cli/plugins/
    plugins_dir = os.path.join(os.path.dirname(__file__), "cli", "plugins")
    _log.info("Searching for plugins in: %s", plugins_dir)

    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = f"app.cli.plugins.{filename[:-3]}"
            try:
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])
                else:
                    importlib.import_module(module_name)
                _log.info("Successfully loaded plugin: %s", module_name)
            except ImportError as e:
                _log.error("Failed to load plugin %s: %s", module_name, e)


# Automatically load all plugins when the application package is first imported.
load_plugins()
