from memory.manager import MemoryManager
from memory.visualize import draw_memory
from input.parser import parse_command, parse_fs, parse_io
from process.scheduler import Scheduler
from files.fs import FileSystem
from iosim.manager import IOManager

def main():
    mm = MemoryManager(64)
    scheduler = Scheduler(mm, quantum=2)
    fs = FileSystem()
    io_mgr = IOManager(lambda pid, dev: scheduler.notify_io_complete(pid, dev))

    print("=== Mini OS — Gestor de Memoria y Procesos ===")
    print("Comandos:")
    print("  create <size> <burst>  (Crear proceso con ráfaga de CPU)")
    print("  tick                   (Avanzar un ciclo de CPU)")
    print("  ps                     (Listar procesos)")
    print("  fs                     (Entrar modo FS: mkfile/open/close/ls)")
    print("  io <pid> <dev> <dur>   (Solicitud E/S: teclado|disco)")
    print("  devices                (Listar dispositivos)")
    print("  alloc <size>           (Asignación manual de memoria)")
    print("  free <pid>")
    print("  lock <start> <size>")
    print("  compact")
    print("  show")
    print("  exit")

    while True:
        cmd = input("\n> ")
        op, arg = parse_command(cmd)

        if op == "error":
            print("Comando inválido.")
            continue

        if op == "exit":
            break

        if op == "create":
            size, burst = arg
            proc = scheduler.create_process(size, burst)
            if proc:
                print(f"Proceso creado: {proc}")
            else:
                print("Error: No hay memoria suficiente.")

        elif op == "tick":
            msg = scheduler.tick()
            io_mgr.tick()
            print(f"[CPU] {msg}")

        elif op == "ps":
            procs = scheduler.get_process_list()
            if not procs:
                print("No hay procesos activos.")
            else:
                print("--- Procesos Activos ---")
                for p in procs:
                    print(p)

        elif op == "fs":
            print("Modo FS. Comandos: mkfile <name> <size>, open <name>, close <name>, ls, exit")
            while True:
                sub = input("fs> ")
                sop, sarg = parse_fs(sub)
                if sop == "error":
                    print("Comando inválido.")
                    continue
                if sub.strip().lower() == "exit":
                    break
                if sop == "mkfile":
                    name, size = sarg
                    ok = fs.create(name, size)
                    print("Creado" if ok else "Ya existe")
                elif sop == "open":
                    ok = fs.open(sarg)
                    print("Abierto" if ok else "No existe")
                elif sop == "close":
                    ok = fs.close(sarg)
                    print("Cerrado" if ok else "No existe")
                elif sop == "ls":
                    items = fs.list()
                    if not items:
                        print("Vacío")
                    else:
                        for f in items:
                            print(f"{f.name} size={f.size} open={f.open}")

        elif op == "devices":
            for name, d in io_mgr.list_devices().items():
                print(f"{name} busy={d.busy} current={d.current} queue={len(d.queue)}")

        elif op == "io":
            pid, dev, dur = arg
            ok = io_mgr.request(pid, dev, dur)
            if not ok:
                print("Dispositivo inválido")
            else:
                blocked = scheduler.block_for_io(pid)
                print("Solicitud enviada" if blocked else "PID no encontrado")

        elif op == "alloc":
            pid = mm.allocate(arg)
            print("PID asignado:" if pid else "No hay espacio.", pid)

        elif op == "free":
            mm.free(arg)
            print("PID liberado")

        elif op == "lock":
            start, size = arg
            ok = mm.lock_region(start, size)
            print("Bloqueado" if ok else "Error bloqueando")

        elif op == "compact":
            mm.compact()
            print("Compactación realizada")

        elif op == "show":
            draw_memory(mm.blocks, mm.total_size, "Estado actual de memoria")

if __name__ == "__main__":
    main()
