def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set((int(p[0]), int(p[1])) for p in (observation.get("self_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    opT = set((int(p[0]), int(p[1])) for p in (observation.get("opponent_territory") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)
    unT = set((int(p[0]), int(p[1])) for p in (observation.get("unclaimed_cells") or []) if isinstance(p, (list, tuple)) and len(p) >= 2)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def local_counts(x, y):
        un, op, se = 0, 0, 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if not inb(nx, ny):
                    continue
                if (nx, ny) in unT:
                    un += 1
                if (nx, ny) in opT:
                    op += 1
                if (nx, ny) in selfT:
                    se += 1
        return un, op, se

    best_move = (0, 0)
    best_val = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        un, opn, sen = local_counts(nx, ny)
        cell_un = 1 if (nx, ny) in unT else 0
        cell_op = 1 if (nx, ny) in opT else 0
        cell_self = 1 if (nx, ny) in selfT else 0

        dist = abs(nx - ox) + abs(ny - oy)
        center_bonus = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0))  # prefer middle

        val = 6 * cell_op + 3 * cell_un + 1 * cell_self
        val += 1.2 * un - 1.0 * opn + 0.4 * sen
        val += 0.03 * (64 - dist)  # advance toward opponent area
        val += 0.02 * center_bonus
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]