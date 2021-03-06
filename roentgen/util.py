"""
Röntgen utility file.

Author: Sergey Vartanov (me@enzet.ru).
"""
from dataclasses import dataclass
from typing import Any


@dataclass
class MinMax:
    """
    Minimum and maximum.
    """
    min_: Any = None
    max_: Any = None

    def update(self, value: Any) -> None:
        """
        Update minimum and maximum with new value.
        """
        self.min_ = value if not self.min_ or value < self.min_ else self.min_
        self.max_ = value if not self.max_ or value > self.max_ else self.max_

    def delta(self) -> Any:
        """
        Difference between maximum and minimum.
        """
        return self.max_ - self.min_

    def center(self) -> Any:
        """
        Get middle point between minimum and maximum.
        """
        return (self.min_ + self.max_) / 2
