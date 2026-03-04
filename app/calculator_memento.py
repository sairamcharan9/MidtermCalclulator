"""
Calculator Memento Module (Undo / Redo)
========================================

Implements the Memento pattern to enable undo and redo of calculator
history state.

Classes:
    - **CalculatorMemento**: a snapshot of the history ``DataFrame``.
    - **MementoCaretaker**: manages undo / redo stacks and coordinates
      with a ``CalculationHistory`` instance.
"""

from __future__ import annotations

import pandas as pd

from app.history import CalculationHistory


class CalculatorMemento:
    """Snapshot of the calculator history state.

    Attributes:
        dataframe: A copy of the history ``DataFrame`` at snapshot time.
    """

    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = dataframe.copy()

    def __repr__(self) -> str:
        return f"CalculatorMemento({len(self.dataframe)} rows)"


class MementoCaretaker:
    """Manages an undo / redo stack of ``CalculatorMemento`` objects.

    Attributes:
        history: The ``CalculationHistory`` instance being managed.
    """

    def __init__(self, history: CalculationHistory) -> None:
        self.history = history
        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []

    def save(self) -> None:
        """Take a snapshot of the current history state.

        Clears the redo stack (new action invalidates future redos).
        """
        snapshot = CalculatorMemento(self.history.get_dataframe())
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo(self) -> bool:
        """Restore the previous history state.

        Returns:
            ``True`` if undo succeeded, ``False`` if nothing to undo.
        """
        if not self._undo_stack:
            return False

        # Save current state for redo
        current = CalculatorMemento(self.history.get_dataframe())
        self._redo_stack.append(current)

        # Restore previous state
        memento = self._undo_stack.pop()
        self.history.set_dataframe(memento.dataframe)
        return True

    def redo(self) -> bool:
        """Re-apply the most recently undone state.

        Returns:
            ``True`` if redo succeeded, ``False`` if nothing to redo.
        """
        if not self._redo_stack:
            return False

        # Save current state for undo
        current = CalculatorMemento(self.history.get_dataframe())
        self._undo_stack.append(current)

        # Restore redo state
        memento = self._redo_stack.pop()
        self.history.set_dataframe(memento.dataframe)
        return True

    @property
    def can_undo(self) -> bool:
        """Whether there is at least one state to undo to."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Whether there is at least one state to redo to."""
        return len(self._redo_stack) > 0

    @property
    def stack_sizes(self) -> tuple[int, int]:
        """Return (undo_stack_size, redo_stack_size)."""
        return len(self._undo_stack), len(self._redo_stack)
