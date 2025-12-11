class Device:
    def __init__(self, name: str):
        self.name = name
        self.busy = False
        self.current = None
        self.remaining = 0
        self.queue = []
