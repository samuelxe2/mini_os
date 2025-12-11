import math
from .blocks import Block
try:
    from mini_os_cpp import merge_buddies as cpp_merge_buddies
except Exception:
    cpp_merge_buddies = None

class MemoryManager:
    def __init__(self, total_size: int):
        # Ensure total_size is power of 2 for Buddy System
        if not self._is_power_of_two(total_size):
            raise ValueError("El tamaño total de memoria debe ser potencia de 2 para el Buddy System.")
            
        self.total_size = total_size
        self.blocks = [Block(0, total_size)]
        self.next_pid = 1

    def _is_power_of_two(self, n):
        return (n != 0) and (n & (n-1) == 0)

    def _next_power_of_two(self, n):
        if n <= 0: return 1
        return 2**(n - 1).bit_length()

    def allocate(self, size: int):
        # Buddy System: Allocate next power of 2
        req_size = self._next_power_of_two(size)
        
        # Find best block
        # We need the smallest free block that is >= req_size
        candidate_idx = None
        min_size_found = float('inf')

        for i, b in enumerate(self.blocks):
            if b.is_free() and b.size >= req_size:
                if b.size < min_size_found:
                    min_size_found = b.size
                    candidate_idx = i
                    # Optimization: if exact match, stop
                    if b.size == req_size:
                        break
        
        if candidate_idx is None:
            return None

        # Split until we match req_size
        while self.blocks[candidate_idx].size > req_size:
            b = self.blocks[candidate_idx]
            new_size = b.size // 2
            
            # Split into two buddies
            buddy1 = Block(b.start, new_size)
            buddy2 = Block(b.start + new_size, new_size)
            
            # Replace current block with these two
            self.blocks[candidate_idx:candidate_idx+1] = [buddy1, buddy2]
            
            # Since we want the first one (lower address) to satisfy the request,
            # we keep pointing to candidate_idx (which is now buddy1).
            # We loop again to check if we need to split further.
            
        # Now blocks[candidate_idx] is exactly req_size
        b = self.blocks[candidate_idx]
        b.pid = self.next_pid
        self.next_pid += 1
        b.locked = False
        
        return b.pid

    def free(self, pid: int):
        # 1. Free the block
        target_idx = None
        for i, b in enumerate(self.blocks):
            if b.pid == pid:
                b.pid = None
                b.locked = False
                target_idx = i
                break
        
        if target_idx is None:
            return # Not found
            
        # 2. Coalesce (Merge buddies recursively)
        self._merge_buddies()

    def _merge_buddies(self):
        if cpp_merge_buddies:
            tuples = [(b.start, b.size, -1 if b.pid is None else b.pid, b.locked) for b in self.blocks]
            merged = cpp_merge_buddies(tuples)
            self.blocks = [Block(t[0], t[1], None if t[2] == -1 else t[2], t[3]) for t in merged]
            return
        while True:
            merged_flag = False
            i = 0
            while i < len(self.blocks) - 1:
                b1 = self.blocks[i]
                b2 = self.blocks[i+1]
                if (b1.is_free() and b2.is_free() and 
                    b1.size == b2.size and 
                    b2.start == (b1.start ^ b1.size)):
                    new_block = Block(b1.start, b1.size * 2)
                    self.blocks[i:i+2] = [new_block]
                    merged_flag = True
                else:
                    i += 1
            if not merged_flag:
                break

    def lock_region(self, start: int, size: int) -> bool:
        # Locking in Buddy System is tricky because it breaks the power-of-2 structure.
        # For simplicity, we will allow locking ONLY if it aligns with existing blocks
        # or we will just mark the blocks that overlap as locked, preventing them from being allocated/merged.
        
        # However, to keep it simple and consistent with previous logic:
        # We will find all blocks in the range and mark them locked.
        # BUT, this might prevent correct merging later.
        
        # Let's implement a "best effort" lock:
        # We walk through blocks. If a block is fully contained in the lock region, lock it.
        # If it partially overlaps... Buddy System doesn't like partial overlaps.
        # We will assume "lock" locks the whole block that contains the range or overlaps.
        
        end = start + size
        affected = False
        
        for b in self.blocks:
            # Check overlap
            if b.start < end and b.end() > start:
                if b.pid is not None:
                    continue # Already used
                b.locked = True
                affected = True
                
        return affected

    def compact(self):
        # Buddy system does not support traditional compaction (moving blocks to one side).
        # It only supports coalescing (merging free buddies).
        # We can trigger a merge scan.
        self._merge_buddies()
