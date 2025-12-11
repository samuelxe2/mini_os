from .fcb import FCB

class FileSystem:
    def __init__(self):
        self.root = {}

    def create(self, name: str, size: int = 0):
        if name in self.root:
            return False
        self.root[name] = FCB(name, size)
        return True

    def open(self, name: str):
        f = self.root.get(name)
        if not f:
            return False
        if f.open:
            return True
        f.open = True
        return True

    def close(self, name: str):
        f = self.root.get(name)
        if not f:
            return False
        f.open = False
        return True

    def list(self):
        return list(self.root.values())
