import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from memory.manager import MemoryManager
from process.scheduler import Scheduler
from files.fs import FileSystem
from iosim.manager import IOManager

def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)

def run():
    print("== Escenario end-to-end ==")
    mm = MemoryManager(64)
    sch = Scheduler(mm, quantum=2)
    fs = FileSystem()
    io = IOManager(lambda pid, dev: sch.notify_io_complete(pid, dev))

    print("Creando procesos...")
    p1 = sch.create_process(8, 3)
    p2 = sch.create_process(16, 3)
    p3 = sch.create_process(8, 3)
    assert_true(p1 and p2 and p3, "Fallo al crear procesos")

    print("Lista de procesos inicial:", sch.get_process_list())
    print("Ejecutando ticks con Round Robin y E/S...")

    # Tick 1: ejecuta p1, luego solicita E/S para p1
    print("[CPU]", sch.tick())
    io.request(p1.pid, "disco", 2)
    sch.block_for_io(p1.pid)
    print("p1 bloqueado por E/S")

    # Tick 2: avanza CPU y E/S
    print("[CPU]", sch.tick())
    io.tick()
    # Tick 3: avanza CPU y E/S (debería completar E/S y volver a READY)
    print("[CPU]", sch.tick())
    io.tick()

    # Verificar que p1 haya salido de WAITING
    states = {p.pid: p.state for p in sch.get_process_list()}
    assert_true(p1.pid in states and states[p1.pid] in ("READY", "RUNNING"), "p1 no regresó de E/S")

    print("Pruebas de FS...")
    assert_true(fs.create("a.txt", 10), "mkfile a.txt")
    assert_true(fs.open("a.txt"), "open a.txt")
    assert_true(fs.close("a.txt"), "close a.txt")
    print("FCBs:", [(f.name, f.size, f.open) for f in fs.list()])

    print("Pruebas de memoria...")
    pid_extra = mm.allocate(5)  # se redondea a 8
    assert_true(pid_extra is not None, "alloc extra")
    mm.free(pid_extra)
    mm.compact()
    print("Bloques de memoria:", [(b.start, b.size, b.pid, b.locked) for b in mm.blocks])

    print("Finalizando ejecución de procesos...")
    for _ in range(10):
        msg = sch.tick()
        io.tick()
        print("[CPU]", msg)
        if msg == "IDLE":
            break
    # Asegurar que todos terminaron
    active = [p for p in sch.get_process_list() if p.state != "TERMINATED"]
    assert_true(len(active) == 0, "Quedaron procesos activos")
    print("OK: Escenario end-to-end completado")

if __name__ == "__main__":
    run()
