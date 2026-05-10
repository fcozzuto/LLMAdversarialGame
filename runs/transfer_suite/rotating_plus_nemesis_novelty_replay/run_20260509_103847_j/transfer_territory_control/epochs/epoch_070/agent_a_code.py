def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                unT.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(cell, S):
        x, y = cell
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in S:
                    c += 1
        return c

    neigh = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    bestv = -10**9

    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine rejects -> stay
            dx, dy = 0, 0
        cell = (nx, ny)
        is_un = cell in unT
        is_op = cell in opT
        is_self = cell in selfT

        a_un = adj_count(cell, unT)
        a_self = adj_count(cell, selfT)
        a_op = adj_count(cell, opT)

        # Prefer expanding into unclaimed, then reclaiming/pressuring opponent, while keeping some contact with our own.
        v = 0
        v += 12 if is_un else 0
        v += 7 if is_op else 0
        v += 2 if is_self else 0
        v += 2 * a_un + 1 * a_self
        v -= 2 * a_op

        # Slightly encourage moving toward nearest unclaimed cell on-board (deterministic, cheap).
        if unT:
            bestd = 10**9
            tx = ty = None
            for (ux, uy) in unT:
                d = abs(ux - nx) + abs(uy - ny)
                if d < bestd:
                    bestd = d
                    tx, ty = ux, uy
            v += max(0, 5 - bestd) if tx is not None else 0

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]