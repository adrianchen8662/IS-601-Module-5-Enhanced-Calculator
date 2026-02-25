########################
# Input Validation     #
########################

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Optional
from app.calculator_config import CalculatorConfig
from app.exceptions import ValidationError

# Matches either a full expression "a op b" or a continuation "op b".
# Group layout:
#   Full:         (1) a   (2) op   (3) b
#   Continuation: (4) op  (5) b
EXPRESSION_PATTERN = re.compile(
    r'([+-]?\s*\d+(?:\.\d+)?)\s*([+\-*/])\s*([+-]?\s*\d+(?:\.\d+)?)'
    r'|([+\-*/])\s*([+-]?\s*\d+(?:\.\d+)?)'
)

@dataclass
class InputValidator:
    """Validates and sanitizes calculator inputs."""
    
    @staticmethod
    def validate_number(value: Any, config: CalculatorConfig) -> Decimal:
        """
        Validate and convert input to Decimal.
        
        Args:
            value: Input value to validate
            config: Calculator configuration
            
        Returns:
            Decimal: Validated and converted number
            
        Raises:
            ValidationError: If input is invalid
        """
        try:
            if isinstance(value, str):
                value = value.strip()
            number = Decimal(str(value))
            if abs(number) > config.max_input_value:
                raise ValidationError(f"Value exceeds maximum allowed: {config.max_input_value}")
            return number.normalize()
        except InvalidOperation as e:
            raise ValidationError(f"Invalid number format: {value}") from e

    @staticmethod
    def validate_expression(raw: str) -> Optional[re.Match]:
        """
        Validate a raw expression string against the calculator input pattern.

        Accepts either a full expression ("a op b") or a continuation ("op b").

        Args:
            raw: The raw input string to validate.

        Returns:
            re.Match: The match object if valid, or None if the input is unrecognized.
        """
        return EXPRESSION_PATTERN.fullmatch(raw)