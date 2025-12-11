from .devices import Device

class IOManager:
    def __init__(self, on_interrupt):
        self.on_interrupt = on_interrupt
        self.devices = {
            "teclado": Device("teclado"),
            "disco": Device("disco"),
        }

    def request(self, pid: int, device_name: str, duration: int):
        d = self.devices.get(device_name)
        if not d:
            return False
        if not d.busy:
            d.busy = True
            d.current = pid
            d.remaining = duration
            return True
        d.queue.append((pid, duration))
        return True

    def tick(self):
        for d in self.devices.values():
            if d.busy:
                d.remaining -= 1
                if d.remaining <= 0:
                    pid = d.current
                    d.busy = False
                    d.current = None
                    d.remaining = 0
                    self.on_interrupt(pid, d.name)
                    if d.queue:
                        pid2, dur2 = d.queue.pop(0)
                        d.busy = True
                        d.current = pid2
                        d.remaining = dur2

    def list_devices(self):
        return self.devices
