########################
# Calculator           #
########################

import logging
from decimal import Decimal
from typing import List, Optional

import pandas as pd

from app.calculation import Calculation, CalculationFactory
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import OperationError, ValidationError
from app.history import HistoryObserver
from app.input_validators import InputValidator
from app.operations import Operation


class Calculator:
    """
    Core calculator that applies the Operation strategy pattern and tracks history.

    Responsibilities:
    - Validate inputs via InputValidator.
    - Execute arithmetic via pluggable Operation strategies.
    - Record each Calculation in a history list.
    - Notify registered HistoryObservers after each calculation.
    - Support undo/redo via CalculatorMemento snapshots.
    - Persist history to and from CSV via CalculatorConfig paths.
    """

    def __init__(self, config: Optional[CalculatorConfig] = None) -> None:
        """
        Initialise the calculator.

        Args:
            config: Optional CalculatorConfig instance. A default config is created
                    when none is provided.

        Raises:
            ConfigurationError: If the provided config fails validation.
        """
        self.config: CalculatorConfig = config or CalculatorConfig()
        self.config.validate()

        self._history: List[Calculation] = []
        self._observers: List[HistoryObserver] = []
        self._undo_stack: List[CalculatorMemento] = []
        self._redo_stack: List[CalculatorMemento] = []
        self._operation: Optional[Operation] = None

    # ------------------------------------------------------------------
    # Observer management
    # ------------------------------------------------------------------

    def add_observer(self, observer: HistoryObserver) -> None:
        """
        Register an observer to be notified after each calculation.

        Args:
            observer: A HistoryObserver instance.

        Raises:
            TypeError: If observer is not a HistoryObserver.
        """
        if not isinstance(observer, HistoryObserver):
            raise TypeError("Observer must be a HistoryObserver instance")
        self._observers.append(observer)

    def _notify_observers(self, calculation: Calculation) -> None:
        """Notify every registered observer about a completed calculation."""
        for observer in self._observers:
            observer.update(calculation)

    # ------------------------------------------------------------------
    # Operation management
    # ------------------------------------------------------------------

    def set_operation(self, operation: Operation) -> None:
        """
        Set the current arithmetic Operation strategy.

        Args:
            operation: An Operation instance (e.g., Addition, Division).
        """
        self._operation = operation

    # ------------------------------------------------------------------
    # Core calculation
    # ------------------------------------------------------------------

    def perform_operation(self, a: str, b: str) -> Decimal:
        """
        Validate inputs, execute the current operation, and record the result.

        Args:
            a: String representation of the first operand.
            b: String representation of the second operand.

        Returns:
            Decimal result of the operation.

        Raises:
            ValidationError: If either input is not a valid number or exceeds the
                             configured maximum.
            OperationError: If no operation has been set, or if the operation itself
                            fails (e.g., division by zero).
        """
        # Validate and parse inputs — raises ValidationError on bad input
        num_a: Decimal = InputValidator.validate_number(a, self.config)
        num_b: Decimal = InputValidator.validate_number(b, self.config)

        if self._operation is None:
            raise OperationError("No operation set. Call set_operation() first.")

        # Snapshot current history for undo before mutating state
        self._undo_stack.append(CalculatorMemento(list(self._history)))
        self._redo_stack.clear()

        try:
            result: Decimal = self._operation.execute(num_a, num_b)
        except (ZeroDivisionError, ValueError, ValidationError) as exc:
            # Roll back the undo snapshot since no calculation was recorded
            self._undo_stack.pop()
            raise OperationError(str(exc)) from exc

        # Record a Calculation entry in history using the factory
        calculation: Calculation = CalculationFactory.create_calculation(
            self._operation.name, float(num_a), float(num_b)
        )
        self._history.append(calculation)
        self._notify_observers(calculation)

        return result

    # ------------------------------------------------------------------
    # History management
    # ------------------------------------------------------------------

    def show_history(self) -> List[Calculation]:
        """Return a copy of the current calculation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the calculation history and reset undo/redo stacks."""
        self._history.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    def undo(self) -> bool:
        """
        Restore history to the state before the most recent calculation.

        Returns:
            True if an undo was performed, False if nothing to undo.
        """
        if not self._undo_stack:
            return False
        self._redo_stack.append(CalculatorMemento(list(self._history)))
        memento = self._undo_stack.pop()
        self._history = list(memento.history)
        return True

    def redo(self) -> bool:
        """
        Re-apply the most recently undone calculation.

        Returns:
            True if a redo was performed, False if nothing to redo.
        """
        if not self._redo_stack:
            return False
        self._undo_stack.append(CalculatorMemento(list(self._history)))
        memento = self._redo_stack.pop()
        self._history = list(memento.history)
        return True

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_history(self) -> None:
        """
        Save the current calculation history to a CSV file.

        The file path is determined by CalculatorConfig.history_file. The
        history directory is created automatically if it does not exist.
        """
        self.config.history_dir.mkdir(parents=True, exist_ok=True)
        records = [
            {
                'operation': calc.operation,
                'operand1': calc.operand1,
                'operand2': calc.operand2,
                'result': calc.result,
            }
            for calc in self._history
        ]
        df = pd.DataFrame(records, columns=['operation', 'operand1', 'operand2', 'result'])
        df.to_csv(self.config.history_file, index=False, encoding=self.config.default_encoding)
        logging.info("History saved to %s", self.config.history_file)

    def load_history(self) -> None:
        """
        Load calculation history from the CSV file specified in CalculatorConfig.

        Silently skips rows that cannot be parsed. Does nothing if the history
        file does not yet exist.
        """
        if not self.config.history_file.exists():
            return

        self._history.clear()
        df = pd.read_csv(self.config.history_file, encoding=self.config.default_encoding)
        for _, row in df.iterrows():
            try:
                calc = CalculationFactory.create_calculation(
                    row['operation'],
                    float(row['operand1']),
                    float(row['operand2']),
                )
                self._history.append(calc)
            except (ValueError, KeyError) as exc:
                logging.warning("Skipping invalid history entry: %s", exc)

        logging.info("History loaded from %s", self.config.history_file)
