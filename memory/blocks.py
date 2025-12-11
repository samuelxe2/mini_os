from dataclasses import dataclass
from typing import Optional

@dataclass
class Block:
    start: int
    size: int
    pid: Optional[int] = None
    locked: bool = False

    def end(self):
        return self.start + self.size

    def is_free(self):
        return self.pid is None and not self.locked
