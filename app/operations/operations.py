class operations:
    # Addition operation
    @staticmethod
    def add(a, b):
        return a + b

    # Subtraction operation
    @staticmethod
    def subtract(a, b):
        return a - b

    # Multiplication operation
    @staticmethod
    def multiply(a, b):
        return a * b

    # Division operation
    @staticmethod
    def divide(a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b