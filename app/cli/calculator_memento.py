"""
Memento Pattern for Undo/Redo Functionality
===========================================

Implements the Memento design pattern to provide undo and redo capabilities
for the calculator's history.
"""

from __future__ import annotations

import pandas as pd

from app.cli.history import CalculationHistory


class CalculatorMemento:
    """
    Represents a snapshot of the calculator's history state (the "Memento").
    Stores an immutable copy of the history DataFrame.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe.copy()

    def __repr__(self) -> str:
        return f"CalculatorMemento(rows={len(self.dataframe)})"


class MementoCaretaker:
    """
    Manages the undo and redo stacks for `CalculatorMemento` objects.
    """

    def __init__(self, history: CalculationHistory) -> None:
        self.history = history
        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []

    def save(self) -> None:
        """Saves the current state of the calculation history to the undo stack."""
        snapshot = CalculatorMemento(self.history.get_dataframe())
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Restores the most recent state from the undo stack."""
        if not self.can_undo:
            return False
        current_state = CalculatorMemento(self.history.get_dataframe())
        self._redo_stack.append(current_state)
        memento = self._undo_stack.pop()
        self.history.set_dataframe(memento.dataframe)
        return True

    def redo(self) -> bool:
        """Restores the most recent state from the redo stack."""
        if not self.can_redo:
            return False
        current_state = CalculatorMemento(self.history.get_dataframe())
        self._undo_stack.append(current_state)
        memento = self._redo_stack.pop()
        self.history.set_dataframe(memento.dataframe)
        return True

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def stack_sizes(self) -> tuple[int, int]:
        return len(self._undo_stack), len(self._redo_stack)
