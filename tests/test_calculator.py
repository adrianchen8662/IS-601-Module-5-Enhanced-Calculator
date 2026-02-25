import pytest
from decimal import Decimal
from unittest.mock import patch

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError
from app.history import LoggingObserver, HistoryObserver
from app.operations import OperationFactory


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

_CALC_ENV_VARS = [
    'CALCULATOR_BASE_DIR',
    'CALCULATOR_HISTORY_DIR',
    'CALCULATOR_HISTORY_FILE',
    'CALCULATOR_LOG_DIR',
    'CALCULATOR_LOG_FILE',
]


@pytest.fixture
def calculator(tmp_path, monkeypatch):
    """Calculator with a temporary base directory and auto-save disabled.

    Environment variables that override CalculatorConfig paths are cleared so
    that the tmp_path is actually used.
    """
    for var in _CALC_ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    config = CalculatorConfig(base_dir=tmp_path, auto_save=False)
    return Calculator(config=config)


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

def test_calculator_initialization(calculator):
    assert calculator.show_history() == []
    assert calculator._undo_stack == []
    assert calculator._redo_stack == []
    assert calculator._operation is None


# ---------------------------------------------------------------------------
# Observer management
# ---------------------------------------------------------------------------

def test_add_observer(calculator):
    observer = LoggingObserver()
    calculator.add_observer(observer)
    assert observer in calculator._observers


def test_add_invalid_observer(calculator):
    with pytest.raises(TypeError, match="Observer must be a HistoryObserver instance"):
        calculator.add_observer("not_an_observer")


def test_observer_notified_after_calculation(calculator):
    notified = []

    class CapturingObserver(HistoryObserver):
        def update(self, calculation):
            notified.append(calculation)

    calculator.add_observer(CapturingObserver())
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    assert len(notified) == 1
    assert notified[0].operation == 'add'


# ---------------------------------------------------------------------------
# Operation management
# ---------------------------------------------------------------------------

def test_set_operation(calculator):
    operation = OperationFactory.create_operation('add')
    calculator.set_operation(operation)
    assert calculator._operation is operation


# ---------------------------------------------------------------------------
# perform_operation
# ---------------------------------------------------------------------------

def test_perform_operation_addition(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    assert calculator.perform_operation('2', '3') == Decimal('5')


def test_perform_operation_subtraction(calculator):
    calculator.set_operation(OperationFactory.create_operation('subtract'))
    assert calculator.perform_operation('10', '4') == Decimal('6')


def test_perform_operation_multiplication(calculator):
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    assert calculator.perform_operation('3', '4') == Decimal('12')


def test_perform_operation_division(calculator):
    calculator.set_operation(OperationFactory.create_operation('divide'))
    assert calculator.perform_operation('10', '2') == Decimal('5')


def test_perform_operation_no_operation_set(calculator):
    with pytest.raises(OperationError, match="No operation set"):
        calculator.perform_operation('2', '3')


def test_perform_operation_invalid_input(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    with pytest.raises(ValidationError):
        calculator.perform_operation('invalid', '3')


def test_perform_operation_division_by_zero(calculator):
    calculator.set_operation(OperationFactory.create_operation('divide'))
    with pytest.raises(OperationError, match="Division by zero is not allowed"):
        calculator.perform_operation('8', '0')


def test_perform_operation_records_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    history = calculator.show_history()
    assert len(history) == 1
    assert history[0].operation == 'add'
    assert history[0].result == 5.0


# ---------------------------------------------------------------------------
# Undo / Redo
# ---------------------------------------------------------------------------

def test_undo_removes_last_entry(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    assert calculator.undo() is True
    assert calculator.show_history() == []


def test_undo_empty_returns_false(calculator):
    assert calculator.undo() is False


def test_redo_reapplies_entry(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    calculator.undo()
    assert calculator.redo() is True
    assert len(calculator.show_history()) == 1


def test_redo_empty_returns_false(calculator):
    assert calculator.redo() is False


def test_undo_redo_sequence(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('1', '1')
    calculator.perform_operation('2', '2')
    calculator.undo()
    assert len(calculator.show_history()) == 1
    calculator.redo()
    assert len(calculator.show_history()) == 2


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

def test_show_history_returns_copy(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    h1 = calculator.show_history()
    h1.clear()
    assert len(calculator.show_history()) == 1


def test_clear_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    calculator.clear_history()
    assert calculator.show_history() == []
    assert calculator._undo_stack == []
    assert calculator._redo_stack == []


# ---------------------------------------------------------------------------
# Persistence (save / load)
# ---------------------------------------------------------------------------

def test_save_and_load_history(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    calculator.save_history()

    calculator.clear_history()
    assert calculator.show_history() == []

    calculator.load_history()
    history = calculator.show_history()
    assert len(history) == 1
    assert history[0].operation == 'add'
    assert history[0].operand1 == 2.0
    assert history[0].operand2 == 3.0


def test_load_history_no_file(calculator):
    """load_history is a no-op when the file does not exist."""
    calculator.load_history()
    assert calculator.show_history() == []


def test_save_history_creates_file(calculator):
    calculator.set_operation(OperationFactory.create_operation('multiply'))
    calculator.perform_operation('3', '4')
    calculator.save_history()
    assert calculator.config.history_file.exists()


# ---------------------------------------------------------------------------
# REPL — expression-based input
# ---------------------------------------------------------------------------

@patch('builtins.input', side_effect=['q'])
@patch('builtins.print')
def test_repl_quit(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call("Exiting")


@patch('builtins.input', side_effect=['h', 'q'])
@patch('builtins.print')
def test_repl_help(mock_print, mock_input):
    calculator_repl()
    printed = ' '.join(
        str(call.args[0]) for call in mock_print.call_args_list if call.args
    )
    assert 'Supported infix operators' in printed


@patch('builtins.input', side_effect=['1 + 2', 'q'])
@patch('builtins.print')
def test_repl_addition(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call('3')


@patch('builtins.input', side_effect=['10 / 2', 'q'])
@patch('builtins.print')
def test_repl_division(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call('5')


@patch('builtins.input', side_effect=['power 2 8', 'q'])
@patch('builtins.print')
def test_repl_power(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call('256')


@patch('builtins.input', side_effect=['9 / 0', 'q'])
@patch('builtins.print')
def test_repl_division_by_zero(mock_print, mock_input):
    calculator_repl()
    printed = ' '.join(
        str(call.args[0]) for call in mock_print.call_args_list if call.args
    )
    assert 'Error' in printed


@patch('builtins.input', side_effect=['1 + 2', 'undo', 'q'])
@patch('builtins.print')
def test_repl_undo(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call('Undone.')


@patch('builtins.input', side_effect=['c', 'q'])
@patch('builtins.print')
def test_repl_clear(mock_print, mock_input):
    calculator_repl()
    mock_print.assert_any_call('Cleared.')


# ---------------------------------------------------------------------------
# Persistence — corrupt CSV rows (calculator.py lines 236-237)
# ---------------------------------------------------------------------------

def test_load_history_skips_corrupt_rows(calculator):
    """Invalid CSV rows are skipped; valid rows are still loaded."""
    calculator.config.history_dir.mkdir(parents=True, exist_ok=True)
    calculator.config.history_file.write_text(
        "operation,operand1,operand2,result\n"
        "add,2,3,5\n"           # valid
        "bad_op,2,3,5\n"        # ValueError: unknown operation
        "add,not_a_num,3,5\n",  # ValueError: float() conversion
        encoding=calculator.config.default_encoding,
    )
    calculator.load_history()
    assert len(calculator.show_history()) == 1
    assert calculator.show_history()[0].operation == 'add'


# ---------------------------------------------------------------------------
# CalculatorMemento (calculator_memento.py lines 34, 53)
# ---------------------------------------------------------------------------

def test_memento_to_dict(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    memento = CalculatorMemento(list(calculator.show_history()))
    d = memento.to_dict()
    assert 'history' in d
    assert 'timestamp' in d
    assert len(d['history']) == 1
    assert d['history'][0]['operation'] == 'add'


def test_memento_from_dict(calculator):
    calculator.set_operation(OperationFactory.create_operation('add'))
    calculator.perform_operation('2', '3')
    memento = CalculatorMemento(list(calculator.show_history()))
    restored = CalculatorMemento.from_dict(memento.to_dict())
    assert len(restored.history) == 1
    assert restored.history[0].operation == 'add'


# ---------------------------------------------------------------------------
# REPL — additional branch coverage
# ---------------------------------------------------------------------------

@patch('builtins.input', side_effect=['1 / 4', 'q'])
@patch('builtins.print')
def test_repl_fractional_result(mock_print, mock_input):
    """_format_result returns str(value) for non-integer results (line 46)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert '0.25' in printed


@patch('builtins.input', side_effect=['history', 'q'])
@patch('builtins.print')
def test_repl_history_empty(mock_print, mock_input):
    """_display_history prints the empty message when no history (lines 50-52)."""
    calculator_repl()
    mock_print.assert_any_call('No calculations in history yet.')


@patch('builtins.input', side_effect=['1 + 2', 'history', 'q'])
@patch('builtins.print')
def test_repl_history_with_entries(mock_print, mock_input):
    """_display_history prints entries when history is non-empty (lines 53-56)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'Calculation History' in printed


@patch('app.calculator_repl.Calculator', side_effect=Exception('init failed'))
@patch('builtins.print')
def test_repl_fatal_init_error(mock_print, mock_calc_class):
    """Fatal Calculator init error is printed and re-raised (lines 71-74)."""
    with pytest.raises(Exception, match='init failed'):
        calculator_repl()
    mock_print.assert_any_call('Fatal error: init failed')


@patch('builtins.input', side_effect=EOFError)
@patch('builtins.print')
def test_repl_eof(mock_print, mock_input):
    """EOFError exits the loop gracefully (lines 83-85)."""
    calculator_repl()
    mock_print.assert_any_call('\nExiting')


@patch('builtins.input', side_effect=['', 'q'])
@patch('builtins.print')
def test_repl_empty_input(mock_print, mock_input):
    """Empty input is ignored and the loop continues (line 88)."""
    calculator_repl()
    mock_print.assert_any_call('Exiting')


@patch('builtins.input', side_effect=['q'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history', side_effect=Exception('disk full'))
def test_repl_quit_save_error(mock_save, mock_print, mock_input):
    """Exception during quit's save_history is swallowed (lines 97-98)."""
    calculator_repl()
    mock_print.assert_any_call('Exiting')


@patch('builtins.input', side_effect=['=', 'q'])
@patch('builtins.print')
def test_repl_show_result_no_result(mock_print, mock_input):
    """= with no prior result prints 'No result yet.' (line 114)."""
    calculator_repl()
    mock_print.assert_any_call('No result yet.')


@patch('builtins.input', side_effect=['1 + 2', '=', 'q'])
@patch('builtins.print')
def test_repl_show_result(mock_print, mock_input):
    """= with a result prints the formatted value (lines 115-116)."""
    calculator_repl()
    mock_print.assert_any_call('= 3')


@patch('builtins.input', side_effect=['undo', 'q'])
@patch('builtins.print')
def test_repl_undo_nothing(mock_print, mock_input):
    """undo with nothing to undo prints the appropriate message (line 129)."""
    calculator_repl()
    mock_print.assert_any_call('Nothing to undo.')


@patch('builtins.input', side_effect=['1 + 2', 'undo', 'redo', 'q'])
@patch('builtins.print')
def test_repl_redo(mock_print, mock_input):
    """Successful redo prints 'Redone.' (lines 133-137)."""
    calculator_repl()
    mock_print.assert_any_call('Redone.')


@patch('builtins.input', side_effect=['redo', 'q'])
@patch('builtins.print')
def test_repl_redo_nothing(mock_print, mock_input):
    """redo with nothing to redo prints the appropriate message (lines 138-139)."""
    calculator_repl()
    mock_print.assert_any_call('Nothing to redo.')


@patch('builtins.input', side_effect=['save', 'q'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history')
def test_repl_save(mock_save, mock_print, mock_input):
    """save command prints confirmation (lines 142-144)."""
    calculator_repl()
    mock_print.assert_any_call('History saved.')


@patch('builtins.input', side_effect=['save', 'q'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history', side_effect=[Exception('disk full'), None])
def test_repl_save_error(mock_save, mock_print, mock_input):
    """Exception during save prints an error message (lines 145-146)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'Error saving history' in printed


@patch('builtins.input', side_effect=['load', 'q'])
@patch('builtins.print')
@patch.object(Calculator, 'load_history')
@patch.object(Calculator, 'show_history', return_value=[])
def test_repl_load(mock_show, mock_load, mock_print, mock_input):
    """load command calls load_history and prints confirmation (lines 150-154)."""
    calculator_repl()
    mock_load.assert_called()
    mock_print.assert_any_call('History loaded.')


@patch('builtins.input', side_effect=['load', 'q'])
@patch('builtins.print')
@patch.object(Calculator, 'save_history')
@patch.object(Calculator, 'load_history', side_effect=Exception('file corrupted'))
def test_repl_load_error(mock_load, mock_save, mock_print, mock_input):
    """Exception during load prints an error message (lines 155-156)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'Error loading history' in printed


@patch('builtins.input', side_effect=['root -4 2', 'q'])
@patch('builtins.print')
def test_repl_root_error(mock_print, mock_input):
    """ValidationError from a keyword operation prints an error (lines 168-169)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'Error' in printed


@patch('builtins.input', side_effect=['xyz abc', 'q'])
@patch('builtins.print')
def test_repl_invalid_input(mock_print, mock_input):
    """Unrecognised input prints the help hint (lines 176-177)."""
    calculator_repl()
    mock_print.assert_any_call("Error: Unrecognised input. Type 'h' for help.")


@patch('builtins.input', side_effect=['+ 3', 'q'])
@patch('builtins.print')
def test_repl_continuation_no_result(mock_print, mock_input):
    """Continuation expression with no prior result prints an error (lines 187-189)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'No previous result' in printed


@patch('builtins.input', side_effect=['1 + 2', '+ 3', 'q'])
@patch('builtins.print')
def test_repl_continuation(mock_print, mock_input):
    """Continuation expression uses the previous result (lines 190-192)."""
    calculator_repl()
    mock_print.assert_any_call('6')


@patch('builtins.input', side_effect=['1 + 2', 'q'])
@patch('builtins.print')
@patch('app.calculator_repl.OperationFactory.create_operation',
       side_effect=Exception('Unexpected'))
def test_repl_unexpected_error(mock_op, mock_print, mock_input):
    """Unhandled exceptions print 'Unexpected error: ...' (lines 200-201)."""
    calculator_repl()
    printed = ' '.join(str(c.args[0]) for c in mock_print.call_args_list if c.args)
    assert 'Unexpected error' in printed
