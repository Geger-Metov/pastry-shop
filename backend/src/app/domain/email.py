import re
from typing import Final

_EMAIL: Final = re.compile(r"^[^@\s]+@[^@\s]+$")


def is_valid_email(val: str) -> bool:
    return _EMAIL.fullmatch(val) is not None
