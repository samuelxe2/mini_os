def parse_command(cmd):
    parts = cmd.strip().split()

    if not parts:
        return None, None

    op = parts[0].lower()

    if op == "create" and len(parts) == 3:
        try:
            size = int(parts[1].replace('<', '').replace('>', ''))
            burst = int(parts[2].replace('<', '').replace('>', ''))
            return "create", (size, burst)
        except ValueError:
            return "error", None

    if op == "tick":
        return "tick", None
        
    if op == "ps":
        return "ps", None
    
    if op == "fs":
        return "fs", None
    
    if op == "io" and len(parts) == 4:
        try:
            pid = int(parts[1].replace('<', '').replace('>', ''))
            dev = parts[2].lower()
            dur = int(parts[3].replace('<', '').replace('>', ''))
            return "io", (pid, dev, dur)
        except ValueError:
            return "error", None

    if op == "alloc" and len(parts) == 2:
        try:
            # Remove potential < > characters if user typed them literally
            clean_arg = parts[1].replace('<', '').replace('>', '')
            return "alloc", int(clean_arg)
        except ValueError:
            return "error", None

    if op == "free" and len(parts) == 2:
        try:
            clean_arg = parts[1].replace('<', '').replace('>', '')
            return "free", int(clean_arg)
        except ValueError:
            return "error", None

    if op == "lock" and len(parts) == 3:
        try:
            clean_arg1 = parts[1].replace('<', '').replace('>', '')
            clean_arg2 = parts[2].replace('<', '').replace('>', '')
            return "lock", (int(clean_arg1), int(clean_arg2))
        except ValueError:
            return "error", None

    if op == "compact":
        return "compact", None

    if op == "show":
        return "show", None

    if op == "exit":
        return "exit", None

    return "error", None

def parse_fs(cmd):
    parts = cmd.strip().split()
    if not parts:
        return None, None
    op = parts[0].lower()
    if op == "mkfile" and len(parts) == 3:
        try:
            name = parts[1]
            size = int(parts[2])
            return "mkfile", (name, size)
        except ValueError:
            return "error", None
    if op == "open" and len(parts) == 2:
        return "open", parts[1]
    if op == "close" and len(parts) == 2:
        return "close", parts[1]
    if op == "ls":
        return "ls", None
    return "error", None

def parse_io(cmd):
    parts = cmd.strip().split()
    if not parts:
        return None, None
    op = parts[0].lower()
    if op == "io" and len(parts) == 4:
        try:
            pid = int(parts[1])
            dev = parts[2].lower()
            dur = int(parts[3])
            return "io", (pid, dev, dur)
        except ValueError:
            return "error", None
    if op == "devices":
        return "devices", None
    return "error", None
