class Process:
    def __init__(self, pid: int, size: int, burst_time: int):
        self.pid = pid
        self.size = size
        self.total_burst = burst_time
        self.remaining_burst = burst_time
        self.state = "READY"  # READY, RUNNING, TERMINATED

    def __repr__(self):
        return f"<PID {self.pid} | Size {self.size} | Burst {self.remaining_burst}/{self.total_burst} | {self.state}>"
