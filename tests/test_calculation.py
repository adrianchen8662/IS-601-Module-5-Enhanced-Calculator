# tests/test_calculations.py
# NOTE: This file was taken from https://github.com/kaw393939/module4_is601/blob/main/tests/test_calculation.py, with some tweaks

"""
Unit tests for the calculator_calculations module using pytest.

This test suite covers both positive and negative scenarios for the Calculation
classes and the CalculationFactory. It ensures that calculations execute correctly,
the factory creates appropriate instances, and error handling behaves as expected.

Tests are organized following the AAA (Arrange, Act, Assert) pattern and adhere
to PEP8 standards for code style and formatting.
"""

import pytest
from unittest.mock import patch
from app.operations.operations import operations
from app.calculation.calculation import (
    CalculationFactory,
    AddCalculation,
    SubtractCalculation,
    MultiplyCalculation,
    DivideCalculation,
    Calculation
)


# -----------------------------------------------------------------------------------
# Test Concrete Calculation Classes
# -----------------------------------------------------------------------------------

@patch.object(operations, 'add')
def test_add_calculation_execute_positive(mock_addition):
    """
    Test the execute method of AddCalculation for a positive scenario.

    This test verifies that the AddCalculation class correctly calls the addition
    method of the Operation class with the provided operands and returns the expected result.
    """
    # Arrange
    a = 10.0  # First operand
    b = 5.0   # Second operand
    expected_result = 15.0  # Expected result of addition
    mock_addition.return_value = expected_result  # Mock the addition method's return value
    add_calc = AddCalculation(a, b)  # Instantiate AddCalculation with operands

    # Act
    result = add_calc.execute()  # Execute the addition calculation

    # Assert
    mock_addition.assert_called_once_with(a, b)  # Ensure addition was called with correct operands
    assert result == expected_result  # Verify the result matches the expected value


@patch.object(operations, 'add')
def test_add_calculation_execute_negative(mock_addition):
    """
    Test the execute method of AddCalculation for a negative scenario.

    This test ensures that if the Operation.addition method raises an exception,
    the AddCalculation.execute method propagates it correctly.
    """
    # Arrange
    a = 10.0
    b = 5.0
    mock_addition.side_effect = Exception("Addition error")  # Simulate an exception in addition
    add_calc = AddCalculation(a, b)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        add_calc.execute()  # Attempt to execute addition, expecting an exception

    # Verify that the exception message is as expected
    assert str(exc_info.value) == "Addition error"


@patch.object(operations, 'subtract')
def test_subtract_calculation_execute_positive(mock_subtraction):
    """
    Test the execute method of SubtractCalculation for a positive scenario.

    This test verifies that the SubtractCalculation class correctly calls the subtraction
    method of the Operation class with the provided operands and returns the expected result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    expected_result = 5.0
    mock_subtraction.return_value = expected_result
    subtract_calc = SubtractCalculation(a, b)

    # Act
    result = subtract_calc.execute()

    # Assert
    mock_subtraction.assert_called_once_with(a, b)
    assert result == expected_result


@patch.object(operations, 'subtract')
def test_subtract_calculation_execute_negative(mock_subtraction):
    """
    Test the execute method of SubtractCalculation for a negative scenario.

    This test ensures that if the Operation.subtraction method raises an exception,
    the SubtractCalculation.execute method propagates it correctly.
    """
    # Arrange
    a = 10.0
    b = 5.0
    mock_subtraction.side_effect = Exception("Subtraction error")
    subtract_calc = SubtractCalculation(a, b)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        subtract_calc.execute()

    # Verify that the exception message is as expected
    assert str(exc_info.value) == "Subtraction error"


@patch.object(operations, 'multiply')
def test_multiply_calculation_execute_positive(mock_multiplication):
    """
    Test the execute method of MultiplyCalculation for a positive scenario.

    This test verifies that the MultiplyCalculation class correctly calls the multiplication
    method of the Operation class with the provided operands and returns the expected result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    expected_result = 50.0
    mock_multiplication.return_value = expected_result
    multiply_calc = MultiplyCalculation(a, b)

    # Act
    result = multiply_calc.execute()

    # Assert
    mock_multiplication.assert_called_once_with(a, b)
    assert result == expected_result


@patch.object(operations, 'multiply')
def test_multiply_calculation_execute_negative(mock_multiplication):
    """
    Test the execute method of MultiplyCalculation for a negative scenario.

    This test ensures that if the Operation.multiplication method raises an exception,
    the MultiplyCalculation.execute method propagates it correctly.
    """
    # Arrange
    a = 10.0
    b = 5.0
    mock_multiplication.side_effect = Exception("Multiplication error")
    multiply_calc = MultiplyCalculation(a, b)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        multiply_calc.execute()

    # Verify that the exception message is as expected
    assert str(exc_info.value) == "Multiplication error"


@patch.object(operations, 'divide')
def test_divide_calculation_execute_positive(mock_division):
    """
    Test the execute method of DivideCalculation for a positive scenario.

    This test verifies that the DivideCalculation class correctly calls the division
    method of the Operation class with the provided operands and returns the expected result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    expected_result = 2.0
    mock_division.return_value = expected_result
    divide_calc = DivideCalculation(a, b)

    # Act
    result = divide_calc.execute()

    # Assert
    mock_division.assert_called_once_with(a, b)
    assert result == expected_result


@patch.object(operations, 'divide')
def test_divide_calculation_execute_negative(mock_division):
    """
    Test the execute method of DivideCalculation for a negative scenario.

    This test ensures that if the Operation.division method raises an exception,
    the DivideCalculation.execute method propagates it correctly.
    """
    # Arrange
    a = 10.0
    b = 5.0
    mock_division.side_effect = Exception("Division error")
    divide_calc = DivideCalculation(a, b)

    # Act & Assert
    with pytest.raises(Exception) as exc_info:
        divide_calc.execute()

    # Verify that the exception message is as expected
    assert str(exc_info.value) == "Division error"


def test_divide_calculation_execute_division_by_zero():
    """
    Test that DivideCalculation.execute raises ZeroDivisionError when dividing by zero.

    This test verifies that attempting to divide by zero using DivideCalculation
    correctly raises a ZeroDivisionError with an appropriate error message.
    """
    # Arrange
    a = 10.0
    b = 0.0
    divide_calc = DivideCalculation(a, b)

    # Act & Assert
    with pytest.raises(ZeroDivisionError) as exc_info:
        divide_calc.execute()

    # Verify the exception message is as expected
    assert str(exc_info.value) == "Cannot divide by zero."


# -----------------------------------------------------------------------------------
# Test CalculationFactory
# -----------------------------------------------------------------------------------

def test_factory_creates_add_calculation():
    """
    Test that CalculationFactory creates an AddCalculation instance.

    This test ensures that the factory correctly instantiates the AddCalculation
    class when the 'add' calculation type is requested.
    """
    # Arrange
    a = 10.0
    b = 5.0

    # Act
    calc = CalculationFactory.create_calculation('add', a, b)

    # Assert
    assert isinstance(calc, AddCalculation)  # Check if the instance is of AddCalculation
    assert calc.a == a                        # Verify the first operand
    assert calc.b == b                        # Verify the second operand


def test_factory_creates_subtract_calculation():
    """
    Test that CalculationFactory creates a SubtractCalculation instance.

    This test verifies that the factory correctly instantiates the SubtractCalculation
    class when the 'subtract' calculation type is requested.
    """
    # Arrange
    a = 10.0
    b = 5.0

    # Act
    calc = CalculationFactory.create_calculation('subtract', a, b)

    # Assert
    assert isinstance(calc, SubtractCalculation)
    assert calc.a == a
    assert calc.b == b


def test_factory_creates_multiply_calculation():
    """
    Test that CalculationFactory creates a MultiplyCalculation instance.

    This test ensures that the factory correctly instantiates the MultiplyCalculation
    class when the 'multiply' calculation type is requested.
    """
    # Arrange
    a = 10.0
    b = 5.0

    # Act
    calc = CalculationFactory.create_calculation('multiply', a, b)

    # Assert
    assert isinstance(calc, MultiplyCalculation)
    assert calc.a == a
    assert calc.b == b


def test_factory_creates_divide_calculation():
    """
    Test that CalculationFactory creates a DivideCalculation instance.

    This test verifies that the factory correctly instantiates the DivideCalculation
    class when the 'divide' calculation type is requested.
    """
    # Arrange
    a = 10.0
    b = 5.0

    # Act
    calc = CalculationFactory.create_calculation('divide', a, b)

    # Assert
    assert isinstance(calc, DivideCalculation)
    assert calc.a == a
    assert calc.b == b


def test_factory_create_unsupported_calculation():
    """
    Test that CalculationFactory raises ValueError when an unsupported calculation type is requested.

    This test ensures that requesting a calculation type not registered with the factory
    results in a ValueError with an appropriate error message.
    """
    # Arrange
    a = 10.0
    b = 5.0
    unsupported_type = 'modulus'  # An unsupported calculation type

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        CalculationFactory.create_calculation(unsupported_type, a, b)

    # Verify that the exception message contains the unsupported type
    assert f"Unsupported calculation type: '{unsupported_type}'" in str(exc_info.value)


def test_factory_register_calculation_duplicate():
    """
    Test that registering a calculation type that's already registered raises ValueError.
    This test verifies that attempting to register a calculation type that has already
    been registered with the factory results in a ValueError to prevent duplicate entries.
    """
    # Arrange & Act
    with pytest.raises(ValueError) as exc_info:
        @CalculationFactory.register_calculation('add')  # Attempt to register 'add' again
        class AnotherAddCalculation(Calculation):
            """
            AnotherAddCalculation attempts to register the 'add' calculation type again.
            """
            def execute(self) -> float:  # pragma: no cover
                return operations.add(self.a, self.b)

    # Assert
    assert "Calculation type 'add' is already registered." in str(exc_info.value)


# -----------------------------------------------------------------------------------
# Test String Representations
# -----------------------------------------------------------------------------------

@patch.object(operations, 'add', return_value=15.0)
def test_calculation_str_representation_addition(mock_addition):
    """
    Test the __str__ method of AddCalculation.

    This test verifies that the string representation of an AddCalculation instance
    is formatted correctly, displaying the class name, operation, operands, and result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    add_calc = AddCalculation(a, b)

    # Act
    calc_str = str(add_calc)

    # Assert
    # Expected string should reflect the operation name derived from the class name ('Add')
    expected_str = f"{add_calc.__class__.__name__}: {a} Add {b} = 15.0"
    assert calc_str == expected_str


@patch.object(operations, 'subtract', return_value=5.0)
def test_calculation_str_representation_subtraction(mock_subtraction):
    """
    Test the __str__ method of SubtractCalculation.

    This test verifies that the string representation of a SubtractCalculation instance
    is formatted correctly, displaying the class name, operation, operands, and result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    subtract_calc = SubtractCalculation(a, b)

    # Act
    calc_str = str(subtract_calc)

    # Assert
    # Expected string should reflect the operation name derived from the class name ('Subtract')
    expected_str = f"{subtract_calc.__class__.__name__}: {a} Subtract {b} = 5.0"
    assert calc_str == expected_str


@patch.object(operations, 'multiply', return_value=50.0)
def test_calculation_str_representation_multiplication(mock_multiplication):
    """
    Test the __str__ method of MultiplyCalculation.

    This test verifies that the string representation of a MultiplyCalculation instance
    is formatted correctly, displaying the class name, operation, operands, and result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    multiply_calc = MultiplyCalculation(a, b)

    # Act
    calc_str = str(multiply_calc)

    # Assert
    # Expected string should reflect the operation name derived from the class name ('Multiply')
    expected_str = f"{multiply_calc.__class__.__name__}: {a} Multiply {b} = 50.0"
    assert calc_str == expected_str


@patch.object(operations, 'divide', return_value=2.0)
def test_calculation_str_representation_division(mock_division):
    """
    Test the __str__ method of DivideCalculation.

    This test verifies that the string representation of a DivideCalculation instance
    is formatted correctly, displaying the class name, operation, operands, and result.
    """
    # Arrange
    a = 10.0
    b = 5.0
    divide_calc = DivideCalculation(a, b)

    # Act
    calc_str = str(divide_calc)

    # Assert
    # Expected string should reflect the operation name derived from the class name ('Divide')
    expected_str = f"{divide_calc.__class__.__name__}: {a} Divide {b} = 2.0"
    assert calc_str == expected_str


def test_calculation_repr_representation_subtraction():
    """
    Test the __repr__ method of SubtractCalculation.

    This test ensures that the repr representation of a SubtractCalculation instance
    accurately reflects the class name and the operands.
    """
    # Arrange
    a = 10.0
    b = 5.0
    subtract_calc = SubtractCalculation(a, b)

    # Act
    calc_repr = repr(subtract_calc)

    # Assert
    # The __repr__ should display the class name and the operands in a clear format
    expected_repr = f"{SubtractCalculation.__name__}(a={a}, b={b})"
    assert calc_repr == expected_repr


def test_calculation_repr_representation_division():
    """
    Test the __repr__ method of DivideCalculation.

    This test ensures that the repr representation of a DivideCalculation instance
    accurately reflects the class name and the operands.
    """
    # Arrange
    a = 10.0
    b = 5.0
    divide_calc = DivideCalculation(a, b)

    # Act
    calc_repr = repr(divide_calc)

    # Assert
    # The __repr__ should display the class name and the operands in a clear format
    expected_repr = f"{DivideCalculation.__name__}(a={a}, b={b})"
    assert calc_repr == expected_repr


# -----------------------------------------------------------------------------------
# Parameterized Tests for Execute Method
# -----------------------------------------------------------------------------------

@pytest.mark.parametrize("calc_type, a, b, expected_result", [
    ('add', 10.0, 5.0, 15.0),
    ('subtract', 10.0, 5.0, 5.0),
    ('multiply', 10.0, 5.0, 50.0),
    ('divide', 10.0, 5.0, 2.0),
])
@patch.object(operations, 'add')
@patch.object(operations, 'subtract')
@patch.object(operations, 'multiply')
@patch.object(operations, 'divide')
def test_calculation_execute_parameterized(
    mock_division, mock_multiplication, mock_subtraction, mock_addition,
    calc_type, a, b, expected_result
):
    """
    Parameterized test for execute method of different Calculation subclasses.

    This test runs multiple scenarios where different calculation types are executed
    with specific operands, verifying that the correct result is returned.
    """
    # Arrange: Set the appropriate mock based on calculation type
    if calc_type == 'add':
        mock_addition.return_value = expected_result
    elif calc_type == 'subtract':
        mock_subtraction.return_value = expected_result
    elif calc_type == 'multiply':
        mock_multiplication.return_value = expected_result
    elif calc_type == 'divide':
        mock_division.return_value = expected_result

    # Act: Create calculation instance and execute
    calc = CalculationFactory.create_calculation(calc_type, a, b)
    result = calc.execute()

    # Assert: Verify the correct operation was called and result matches
    if calc_type == 'add':
        mock_addition.assert_called_once_with(a, b)
    elif calc_type == 'subtract':
        mock_subtraction.assert_called_once_with(a, b)
    elif calc_type == 'multiply':
        mock_multiplication.assert_called_once_with(a, b)
    elif calc_type == 'divide':
        mock_division.assert_called_once_with(a, b)

    assert result == expected_result


# -----------------------------------------------------------------------------------
# Parameterized Tests for String Representation
# -----------------------------------------------------------------------------------

@pytest.mark.parametrize("calc_type, a, b, expected_str", [
    ('add', 10.0, 5.0, "AddCalculation: 10.0 Add 5.0 = 15.0"),
    ('subtract', 10.0, 5.0, "SubtractCalculation: 10.0 Subtract 5.0 = 5.0"),
    ('multiply', 10.0, 5.0, "MultiplyCalculation: 10.0 Multiply 5.0 = 50.0"),
    ('divide', 10.0, 5.0, "DivideCalculation: 10.0 Divide 5.0 = 2.0"),
])
@patch.object(operations, 'add', return_value=15.0)
@patch.object(operations, 'subtract', return_value=5.0)
@patch.object(operations, 'multiply', return_value=50.0)
@patch.object(operations, 'divide', return_value=2.0)
def test_calculation_str_parameterized(
    mock_division, mock_multiplication, mock_subtraction, mock_addition,
    calc_type, a, b, expected_str
):
    """
    Parameterized test for __str__ method of Calculation subclasses.

    This test verifies that the string representation of different Calculation instances
    is formatted correctly, displaying the class name, operation, operands, and result.
    """
    # Arrange: No additional setup needed as mocks are already set via decorators

    # Act: Create calculation instance and get string representation
    calc = CalculationFactory.create_calculation(calc_type, a, b)
    calc_str = str(calc)

    # Assert: Verify the string representation matches the expected format
    assert calc_str == expected_str