import pytest
from app.calculation import Calculation, CalculationFactory
from app.exceptions import ValidationError


# ---------------------------------------------------------------------------
# Basic arithmetic
# ---------------------------------------------------------------------------

def test_addition():
    calc = CalculationFactory.create_calculation('add', 2.0, 3.0)
    assert calc.result == 5.0


def test_subtraction():
    calc = CalculationFactory.create_calculation('subtract', 5.0, 3.0)
    assert calc.result == 2.0


def test_multiplication():
    calc = CalculationFactory.create_calculation('multiply', 4.0, 2.0)
    assert calc.result == 8.0


def test_division():
    calc = CalculationFactory.create_calculation('divide', 8.0, 2.0)
    assert calc.result == 4.0


def test_power():
    calc = CalculationFactory.create_calculation('power', 2.0, 3.0)
    assert calc.result == 8.0


def test_root():
    calc = CalculationFactory.create_calculation('root', 16.0, 2.0)
    assert calc.result == 4.0


# ---------------------------------------------------------------------------
# Error cases (errors raised when result is accessed)
# ---------------------------------------------------------------------------

def test_division_by_zero():
    calc = CalculationFactory.create_calculation('divide', 8.0, 0.0)
    with pytest.raises(ValidationError, match="Division by zero is not allowed"):
        _ = calc.result


def test_negative_power():
    calc = CalculationFactory.create_calculation('power', 2.0, -3.0)
    with pytest.raises(ValidationError, match="Negative exponents not supported"):
        _ = calc.result


def test_invalid_root_negative_base():
    calc = CalculationFactory.create_calculation('root', -16.0, 2.0)
    with pytest.raises(ValidationError, match="Cannot calculate root of negative number"):
        _ = calc.result


def test_invalid_root_zero_degree():
    calc = CalculationFactory.create_calculation('root', 9.0, 0.0)
    with pytest.raises(ValidationError, match="Zero root is undefined"):
        _ = calc.result


def test_unknown_operation():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.create_calculation('unknown', 5.0, 3.0)


# ---------------------------------------------------------------------------
# Observer-compatible properties
# ---------------------------------------------------------------------------

def test_operation_property():
    calc = CalculationFactory.create_calculation('add', 2.0, 3.0)
    assert calc.operation == 'add'


def test_operand_properties():
    calc = CalculationFactory.create_calculation('subtract', 10.0, 4.0)
    assert calc.operand1 == 10.0
    assert calc.operand2 == 4.0


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

def test_to_dict():
    calc = CalculationFactory.create_calculation('add', 2.0, 3.0)
    assert calc.to_dict() == {
        'operation': 'add',
        'operand1': 2.0,
        'operand2': 3.0,
        'result': 5.0,
    }


def test_from_dict():
    data = {'operation': 'add', 'operand1': 2.0, 'operand2': 3.0}
    calc = Calculation.from_dict(data)
    assert calc.operation == 'add'
    assert calc.operand1 == 2.0
    assert calc.operand2 == 3.0
    assert calc.result == 5.0


def test_from_dict_invalid_operand():
    data = {'operation': 'add', 'operand1': 'invalid', 'operand2': '3'}
    with pytest.raises((ValueError, TypeError)):
        Calculation.from_dict(data)


# ---------------------------------------------------------------------------
# String representations
# ---------------------------------------------------------------------------

def test_str_representation():
    calc = CalculationFactory.create_calculation('add', 2.0, 3.0)
    s = str(calc)
    assert 'AddCalculation' in s
    assert '5' in s


def test_repr_representation():
    calc = CalculationFactory.create_calculation('add', 2.0, 3.0)
    assert repr(calc) == 'AddCalculation(a=2.0, b=3.0)'


# ---------------------------------------------------------------------------
# CalculationFactory registration guard
# ---------------------------------------------------------------------------

def test_register_duplicate_raises():
    with pytest.raises(ValueError, match="already registered"):
        CalculationFactory.register_calculation('add')(
            CalculationFactory._calculations['add']
        )
