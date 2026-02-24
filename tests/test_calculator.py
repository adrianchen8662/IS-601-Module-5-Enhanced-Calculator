""" tests/test_calculator_coverage.py """
import sys
from io import StringIO
from unittest.mock import patch
from app.calculator import calculator
from app.calculator.calculator import format_result, display_history, parse_number
from app.calculation.calculation import AddCalculation


# NOTE: Reused helper pattern from test_calculator.py
def run_calculator_with_input(monkeypatch, inputs):
    """
    Simulates user input and captures output from the calculator REPL.

    :param monkeypatch: pytest fixture to simulate user input
    :param inputs: list of inputs to simulate
    :return: captured output as a string
    """
    input_iterator = iter(inputs)
    monkeypatch.setattr('builtins.input', lambda _: next(input_iterator))
    captured_output = StringIO()
    sys.stdout = captured_output
    calculator()
    sys.stdout = sys.__stdout__
    return captured_output.getvalue()


# --- Basic operations ---

def test_addition(monkeypatch):
    """Test addition full expression."""
    output = run_calculator_with_input(monkeypatch, ["1 + 2", "q"])
    assert "3" in output

def test_subtraction(monkeypatch):
    """Test subtraction full expression."""
    output = run_calculator_with_input(monkeypatch, ["10 - 4", "q"])
    assert "6" in output

def test_multiplication(monkeypatch):
    """Test multiplication full expression."""
    output = run_calculator_with_input(monkeypatch, ["4 * 5", "q"])
    assert "20" in output

def test_division(monkeypatch):
    """Test division full expression."""
    output = run_calculator_with_input(monkeypatch, ["10 / 2", "q"])
    assert "5" in output

def test_float_result(monkeypatch):
    """Test that non-integer results are shown as floats."""
    output = run_calculator_with_input(monkeypatch, ["1 / 3", "q"])
    assert "." in output  # e.g. 0.3333...


# --- Continuation ---

def test_continuation(monkeypatch):
    """Test continuing from a previous result."""
    output = run_calculator_with_input(monkeypatch, ["1 + 2", "+ 5", "q"])
    assert "3" in output
    assert "8" in output

def test_continuation_no_previous_result(monkeypatch):
    """Test continuation with no prior result gives an error."""
    output = run_calculator_with_input(monkeypatch, ["+ 5", "q"])
    assert "Error: No previous result" in output


# --- = command ---

def test_equals_with_result(monkeypatch):
    """Test = shows the current result."""
    output = run_calculator_with_input(monkeypatch, ["3 + 3", "=", "q"])
    assert output.count("6") >= 2  # once from expression, once from =

def test_equals_no_result(monkeypatch):
    """Test = with no result yet."""
    output = run_calculator_with_input(monkeypatch, ["=", "q"])
    assert "No result yet." in output


# --- clear ---

def test_clear(monkeypatch):
    """Test clear resets the result and history."""
    output = run_calculator_with_input(monkeypatch, ["3 + 3", "c", "=", "q"])
    assert "Cleared." in output
    assert "No result yet." in output

def test_clear_alias(monkeypatch):
    """Test 'clear' alias works the same as 'c'."""
    output = run_calculator_with_input(monkeypatch, ["3 + 3", "clear", "=", "q"])
    assert "Cleared." in output

def test_clear_also_wipes_history(monkeypatch):
    """Test that clear wipes history so subsequent history command shows empty."""
    output = run_calculator_with_input(monkeypatch, ["3 + 3", "c", "history", "q"])
    assert "No calculations in history yet." in output


# --- help ---

def test_help(monkeypatch):
    """Test h prints help text."""
    output = run_calculator_with_input(monkeypatch, ["h", "q"])
    assert "Calculator REPL" in output

def test_help_alias(monkeypatch):
    """Test 'help' alias prints help text."""
    output = run_calculator_with_input(monkeypatch, ["help", "q"])
    assert "Calculator REPL" in output


# --- quit ---

def test_quit(monkeypatch):
    """Test q exits with message."""
    output = run_calculator_with_input(monkeypatch, ["q"])
    assert "Exiting" in output

def test_quit_alias(monkeypatch):
    """Test 'quit' alias exits."""
    output = run_calculator_with_input(monkeypatch, ["quit"])
    assert "Exiting" in output


# --- Empty input ---

def test_empty_input(monkeypatch):
    """Test that empty input is ignored and loop continues."""
    output = run_calculator_with_input(monkeypatch, ["", "q"])
    assert "Exiting" in output


# --- Error cases ---

def test_unrecognized_input(monkeypatch):
    """Test that unrecognized input prints an error."""
    output = run_calculator_with_input(monkeypatch, ["hello world", "q"])
    assert "Error: Unrecognized input" in output

def test_division_by_zero(monkeypatch):
    """Test division by zero prints an error."""
    output = run_calculator_with_input(monkeypatch, ["5 / 0", "q"])
    assert "Error:" in output

def test_invalid_number_in_expression():
    """Test that a non-numeric value in parse_number raises ValueError."""
    import pytest
    with pytest.raises(ValueError, match="Not a valid number"):
        parse_number("abc")


# --- EOFError / KeyboardInterrupt ---

def test_eoferror_exits(monkeypatch):
    """Test that EOFError exits gracefully."""
    monkeypatch.setattr('builtins.input', lambda _: (_ for _ in ()).throw(EOFError))
    captured_output = StringIO()
    sys.stdout = captured_output
    calculator()
    sys.stdout = sys.__stdout__
    assert "Exiting" in captured_output.getvalue()

def test_keyboardinterrupt_exits(monkeypatch):
    """Test that KeyboardInterrupt exits gracefully."""
    monkeypatch.setattr('builtins.input', lambda _: (_ for _ in ()).throw(KeyboardInterrupt))
    captured_output = StringIO()
    sys.stdout = captured_output
    calculator()
    sys.stdout = sys.__stdout__
    assert "Exiting" in captured_output.getvalue()


# --- format_result ---

def test_format_result_integer_float():
    """Test that a float with no fractional part is rendered without '.0'."""
    # Arrange & Act
    result = format_result(4.0)

    # Assert
    assert result == "4"

def test_format_result_non_integer_float():
    """Test that a float with a fractional part is rendered as-is."""
    # Arrange & Act
    result = format_result(3.5)

    # Assert
    assert result == "3.5"

def test_format_result_non_float_value():
    """
    Test the else branch of format_result where the value is not a float instance.
    This covers the branch where isinstance(value, float) is False.
    """
    # Arrange & Act
    result = format_result(7)  # plain int, not a float

    # Assert
    assert result == "7"


# --- display_history ---

def test_display_history_empty(capsys):
    """Test that display_history prints the empty message when history is empty."""
    # Arrange
    history = []

    # Act
    display_history(history)

    # Assert
    captured = capsys.readouterr()
    assert "No calculations in history yet." in captured.out

def test_display_history_with_items(capsys):
    """
    Test that display_history prints each calculation when history contains entries.
    This covers the populated history branch (print loop).
    """
    # Arrange: build a real Calculation object so __str__ works correctly
    calc = AddCalculation(3.0, 4.0)
    history = [calc]

    # Act
    display_history(history)

    # Assert
    captured = capsys.readouterr()
    assert "Calculation History:" in captured.out
    assert "1." in captured.out
    assert "AddCalculation" in captured.out

def test_display_history_multiple_items(capsys):
    """Test that display_history numbers multiple entries correctly."""
    # Arrange
    history = [AddCalculation(1.0, 2.0), AddCalculation(3.0, 4.0)]

    # Act
    display_history(history)

    # Assert
    captured = capsys.readouterr()
    assert "1." in captured.out
    assert "2." in captured.out


# --- history / hist commands in the REPL ---

def test_history_command_empty(monkeypatch):
    """Test 'history' command before any calculations shows empty message."""
    output = run_calculator_with_input(monkeypatch, ["history", "q"])
    assert "No calculations in history yet." in output

def test_hist_alias_empty(monkeypatch):
    """Test 'hist' alias shows empty history message."""
    output = run_calculator_with_input(monkeypatch, ["hist", "q"])
    assert "No calculations in history yet." in output

def test_history_command_with_entries(monkeypatch):
    """
    Test 'history' after a calculation shows the recorded entry.
    This covers the populated branch of display_history via the REPL path.
    """
    output = run_calculator_with_input(monkeypatch, ["3 + 4", "history", "q"])
    assert "Calculation History:" in output
    assert "1." in output

def test_hist_alias_with_entries(monkeypatch):
    """Test 'hist' alias shows history entries after a calculation."""
    output = run_calculator_with_input(monkeypatch, ["2 * 5", "hist", "q"])
    assert "Calculation History:" in output
    assert "1." in output


# --- Prompt with result ---

def test_prompt_shows_result_after_calculation(monkeypatch):
    """
    Test that after a calculation the prompt includes the current result.
    The bracketed prompt '[N] > ' is rendered on the second iteration of the
    loop, so we capture what is passed to input() to verify.
    """
    # After '2 + 3' the result is 5; the next input() call receives the '[5] > ' prompt.
    prompts = []
    inputs = iter(["2 + 3", "q"])

    def fake_input(prompt):
        prompts.append(prompt)
        return next(inputs)

    monkeypatch.setattr('builtins.input', fake_input)
    captured_output = StringIO()
    sys.stdout = captured_output
    calculator()
    sys.stdout = sys.__stdout__

    # The first prompt is '> ', the second (after the result is set) should contain '5'
    assert len(prompts) == 2
    assert "5" in prompts[1]


# --- except ValueError in REPL ---

def test_repl_catches_value_error_from_factory(monkeypatch):
    """
    Test that a ValueError raised by CalculationFactory is caught and printed.
    We patch CalculationFactory.create_calculation to raise ValueError so the
    except ValueError branch is executed.
    """
    with patch(
        'app.calculator.calculator.CalculationFactory.create_calculation',
        side_effect=ValueError("mocked factory error")
    ):
        output = run_calculator_with_input(monkeypatch, ["1 + 2", "q"])

    assert "Error: mocked factory error" in output