def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    role = (observation.get("self_role") or "").lower()
    is_evader = "evader" in role

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    dirs = [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def adj_block_pen(x, y):
        p = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in blocked:
                p += 2
        return p

    best = None
    bestv = None
    eps = 1e-9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)
        edge = min(nx, ny, w - 1 - nx, h - 1 - ny)

        # If pursuer can capture immediately, do it.
        if not is_evader and nx == ox and ny == oy:
            val = -1e18
        else:
            # Obstacle-aware tie-breaking.
            pen = adj_block_pen(nx, ny)
            if is_evader:
                # Maximize distance; also prefer staying away from edges a bit.
                val = (cheb * 1000) + (edge * 2) - (pen * 5) + (1.0 / (man + 1 + eps))
            else:
                # Minimize distance; slight preference for center and avoiding adjacent obstacles.
                val = (-cheb * 1000) - (man * 3) + (edge * 1.5) - (pen * 5)

        if bestv is None or (val < bestv if not is_evader else val > bestv):
            bestv = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best