def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def cells_from(key):
        out = []
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    out.append((x, y))
        return out

    targets = cells_from("unclaimed_cells")
    if not targets:
        targets = cells_from("resources")
    if not targets:
        targets = [(ox, oy)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    neigh = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    best = None
    best_key = None
    for dx, dy in neigh:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        t = min(abs(nx - tx) + abs(ny - ty) for tx, ty in targets)
        # Prefer reducing distance to nearest target; if tied, prefer moving toward opponent's distance reduction.
        opp = abs(nx - ox) + abs(ny - oy)
        key = (t, opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best