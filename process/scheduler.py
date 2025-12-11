from .pcb import Process

class Scheduler:
    def __init__(self, memory_manager, quantum: int = 2):
        self.mm = memory_manager
        self.ready_queue = []
        self.running_process = None
        self.terminated_processes = []
        self.waiting_processes = []
        self.quantum = quantum
        self.slice = 0

    def create_process(self, size: int, burst: int):
        pid = self.mm.allocate(size)
        if pid is None:
            return None
        new_proc = Process(pid, size, burst)
        self.ready_queue.append(new_proc)
        return new_proc

    def tick(self):
        if not self.running_process:
            if self.ready_queue:
                self.running_process = self.ready_queue.pop(0)
                self.running_process.state = "RUNNING"
                self.slice = self.quantum
            else:
                return "IDLE"

        proc = self.running_process
        proc.remaining_burst -= 1
        self.slice -= 1

        msg = f"Ejecutando PID {proc.pid} (Restante: {proc.remaining_burst})"

        if proc.remaining_burst <= 0:
            proc.state = "TERMINATED"
            self.terminated_processes.append(proc)
            self.mm.free(proc.pid)
            self.running_process = None
            msg += " -> TERMINADO (Memoria liberada)"
        elif self.slice <= 0:
            proc.state = "READY"
            self.ready_queue.append(proc)
            self.running_process = None
            msg += " -> CAMBIO DE CONTEXTO"
            
        return msg

    def get_process_list(self):
        all_procs = []
        if self.running_process:
            all_procs.append(self.running_process)
        all_procs.extend(self.ready_queue)
        all_procs.extend(self.waiting_processes)
        return all_procs

    def block_for_io(self, pid: int):
        if self.running_process and self.running_process.pid == pid:
            p = self.running_process
            p.state = "WAITING"
            self.waiting_processes.append(p)
            self.running_process = None
            return True
        for i, p in enumerate(self.ready_queue):
            if p.pid == pid:
                p.state = "WAITING"
                self.waiting_processes.append(p)
                self.ready_queue.pop(i)
                return True
        return False

    def notify_io_complete(self, pid: int, device_name: str):
        for i, p in enumerate(self.waiting_processes):
            if p.pid == pid:
                p.state = "READY"
                self.ready_queue.append(p)
                self.waiting_processes.pop(i)
                return True
        return False
