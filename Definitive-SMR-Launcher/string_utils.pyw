"""
string_utils.py

Utility functions for string manipulation.
"""
import __main__  # Access main's globals and imports

def string_utils(input_string: str, max_length: int = 100, placeholder: str = "...") -> str:
    """
    Truncate a string to a maximum length, appending a placeholder if truncated.

    Parameters:
        input_string (str): The string to truncate.
        max_length (int): Maximum allowed length of the string including placeholder.
        placeholder (str): The string to append when truncating (default "...").

    Returns:
        str: The truncated string if it exceeds max_length, else the original string.
    """
    __main__.error_logs(f"[string_utils] resize string " + str(input_string),"info")
    if len(input_string) > max_length:
        return input_string[: max_length - len(placeholder)] + placeholder
    return input_string