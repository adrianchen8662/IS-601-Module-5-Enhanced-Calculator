import re
from typing import List, Optional
from app.operations.operations import operations
from app.calculation.calculation import Calculation, CalculationFactory

# Maps infix operator symbols to their CalculationFactory type strings,
# allowing us to bridge the user-facing syntax (+, -, *, /) with the
# factory's registered calculation types (add, subtract, multiply, divide).
OPERATOR_MAP = {
    '+': 'add',
    '-': 'subtract',
    '*': 'multiply',
    '/': 'divide',
}

HELP_TEXT = \
"""
Calculator REPL
---------------
Usage:
  <num> <op> <num>      Start a new expression e.g. 1 + 2
  <op> <num>            Continue from last result e.g. + 5
  =                     Show current result
  history / hist        Show calculation history
  c / clear             Clear result and history
  h / help              Show this help
  q / quit              Exit

Supported operators: + - * /
"""

# Define a type alias
def parse_number(s: str) -> float:
    try:
        return float(s.replace(' ', ''))
    except ValueError:
        raise ValueError(f"Not a valid number: '{s}'")


def format_result(value: float) -> str:
    # Remove extra zeroes if integer
    return str(int(value) if isinstance(value, float) and value.is_integer() else value)


def display_history(history: List[Calculation]) -> None:
    if not history:
        print("No calculations in history yet.")
        return
    print("\nCalculation History:")
    for idx, calc in enumerate(history, start=1):
        print(f"  {idx}. {calc}")
    print()


# REPL Interface
def calculator() -> None:
    result: Optional[float] = None

    # Initialize an empty list to keep track of calculation history
    history: List[Calculation] = []

    print(HELP_TEXT)

    while True:
        # Show prompt with current result if available
        prompt = f"[{format_result(result)}] > " if result is not None else "> "
        try:
            raw = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting")
            break

        if not raw:
            continue

        cmd = raw.lower()

        # Quit
        if cmd in ('q', 'quit'):
            print("Exiting")
            break

        # Help
        if cmd in ('h', 'help'):
            print(HELP_TEXT)
            continue

        # Clear results and history
        if cmd in ('c', 'clear'):
            result = None
            history.clear()
            print("Cleared.")
            continue

        # Get current running total
        if cmd == '=':
            if result is None:
                print("No result yet.")
            else:
                print(f"= {format_result(result)}")
            continue

        # Show history of calculations performed during the session
        if cmd in ('history', 'hist'):
            display_history(history)
            continue

        # Regex to check valid expression for input validation
        match = re.fullmatch(
            r'([+-]?\s*\d+(?:\.\d+)?)\s*([+\-*/])\s*([+-]?\s*\d+(?:\.\d+)?)'
            r'|([+\-*/])\s*([+-]?\s*\d+(?:\.\d+)?)',
            raw
        )
        if not match:
            print("Error: Unrecognized input. Type 'h' for help.")
            continue

        try:
            # If full expression
            if match.group(1) is not None:
                a = parse_number(match.group(1))
                op_symbol = match.group(2)
                b = parse_number(match.group(3))
            # Else continuation from last result
            else:
                if result is None:
                    print("Error: No previous result. Start with a full expression, e.g. '1 + 2'.")
                    continue
                a = result
                op_symbol = match.group(4)
                b = parse_number(match.group(5))

            # Create and execute a Calculation instance using the factory
            calc_type = OPERATOR_MAP[op_symbol]
            calculation: Calculation = CalculationFactory.create_calculation(calc_type, a, b)
            result = calculation.execute()

            # Append the calculation object to history and print result
            history.append(calculation)
            print(format_result(result))

        except ZeroDivisionError:
            print("Error: Cannot divide by zero.")
        except ValueError as e:
            print(f"Error: {e}")