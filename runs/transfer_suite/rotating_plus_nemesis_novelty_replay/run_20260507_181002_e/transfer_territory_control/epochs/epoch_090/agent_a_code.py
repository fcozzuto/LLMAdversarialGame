def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def cells(v):
        s = []
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.append((int(p[0]), int(p[1])))
        return s

    obstacles = set(cells(observation.get("obstacles")))
    resources = cells(observation.get("resources"))
    unclaimed = cells(observation.get("unclaimed_cells"))
    selfT = set(cells(observation.get("self_territory")))
    oppT = set(cells(observation.get("opponent_territory")))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d(x1, y1, x2, y2): 
        dx = x1 - x2
        dy = y1 - y2
        return (dx if dx >= 0 else -dx) + (dy if dy >= 0 else -dy)

    targets = resources[:]
    if not targets and unclaimed:
        targets = unclaimed[:]
    if not targets and oppT:
        tx, ty = ox, oy
    else:
        tx, ty = None, None

    best = None
    bestv = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = 0
        if targets:
            best_r = None
            for (rx, ry) in targets:
                if (rx, ry) in obstacles:
                    continue
                if (rx, ry) == (nx, ny):
                    best_r = 0
                    break
                dd = d(nx, ny, rx, ry)
                if best_r is None or dd < best_r:
                    best_r = dd
            v += 10000 - (best_r if best_r is not None else 10**9)
        else:
            v += -d(nx, ny, tx, ty) if tx is not None else 0

        v += 3 * d(nx, ny, ox, oy)  # keep distance from opponent
        if (nx, ny) in oppT:
            v -= 10000
        if (nx, ny) in selfT:
            v += 50
        v -= 1 if dx == 0 and dy == 0 else 0

        if best is None or v > bestv:
            best = [dx, dy]
            bestv = v

    return best if best is not None else [0, 0]