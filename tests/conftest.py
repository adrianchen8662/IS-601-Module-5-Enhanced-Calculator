# tests/conftest.py

# NOTE: This file was taken from https://github.com/kaw393939/module4_is601/blob/main/tests/conftest.py, with some tweaks

import pytest
from app.calculation.calculation import CalculationFactory
from app.calculation.calculation import (
    AddCalculation,
    SubtractCalculation,
    MultiplyCalculation,
    DivideCalculation,
    
)

@pytest.fixture(autouse=True)
def reset_calculation_factory():
    """
    Fixture to reset CalculationFactory's registered calculations before each test.
    """
    # Clear existing registrations
    CalculationFactory._calculations.clear()

    # Re-register the default calculations
    CalculationFactory.register_calculation('add')(AddCalculation)
    CalculationFactory.register_calculation('subtract')(SubtractCalculation)
    CalculationFactory.register_calculation('multiply')(MultiplyCalculation)
    CalculationFactory.register_calculation('divide')(DivideCalculation)