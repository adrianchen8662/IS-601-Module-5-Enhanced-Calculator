########################
# Operation Classes    #
########################

from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict

from app.exceptions import ValidationError


class Operation(ABC):
    """
    Abstract base class for calculator operations.

    Defines the interface for all arithmetic operations. Each operation must
    implement the execute method and can optionally override operand validation.
    """

    name: str = ''

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """
        Execute the operation.

        Args:
            a (Decimal): First operand.
            b (Decimal): Second operand.

        Returns:
            Decimal: Result of the operation.
        """
        pass  # pragma: no cover

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        """
        Validate operands before execution.

        Can be overridden by subclasses to enforce operation-specific rules.

        Raises:
            ValidationError: If operands are invalid for this operation.
        """
        pass

    def __str__(self) -> str:
        return self.__class__.__name__


class Addition(Operation):
    """Addition operation implementation."""

    name = 'add'

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b


class Subtraction(Operation):
    """Subtraction operation implementation."""

    name = 'subtract'

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b


class Multiplication(Operation):
    """Multiplication operation implementation."""

    name = 'multiply'

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b


class Division(Operation):
    """Division operation implementation."""

    name = 'divide'

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b


class Power(Operation):
    """Exponentiation operation implementation."""

    name = 'power'

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))


class Root(Operation):
    """Root (nth root) operation implementation."""

    name = 'root'

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))


class OperationFactory:
    """
    Factory class for creating operation instances.

    Implements the Factory pattern by providing a method to instantiate
    different operation classes based on a given operation type. This promotes
    scalability and decouples the creation logic from the Calculator class.
    """

    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        """
        Register a new operation type.

        Args:
            name (str): Operation identifier (e.g., 'modulus').
            operation_class (type): The class implementing the new operation.

        Raises:
            TypeError: If operation_class does not inherit from Operation.
        """
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        """
        Create an operation instance based on the operation type.

        Args:
            operation_type (str): The type of operation to create (e.g., 'add').

        Returns:
            Operation: An instance of the specified operation class.

        Raises:
            ValueError: If the operation type is unknown.
        """
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()
