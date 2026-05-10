def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])[:2]
    ox, oy = observation.get("opponent_position", [0, 0])[:2]
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is not None and len(p) >= 2:
            try:
                obstacles.add((int(p[0]), int(p[1])))
            except:
                pass

    resources = observation.get("resources", []) or []
    resources_xy = []
    for r in resources:
        if r is None:
            continue
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            try:
                resources_xy.append((int(r[0]), int(r[1])))
            except:
                pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    if not resources_xy:
        # deterministic safe-ish move: maximize distance from opponent
        best = None
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d1 = abs(nx - ox) + abs(ny - oy)
            key = (d1, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    # pick target: nearest resource by manhattan, tie by coordinates
    tx, ty = resources_xy[0]
    bestd = abs(sx - tx) + abs(sy - ty)
    for rx, ry in resources_xy[1:]:
        d = abs(sx - rx) + abs(sy - ry)
        if d < bestd or (d == bestd and (rx, ry) < (tx, ty)):
            bestd = d
            tx, ty = rx, ry

    # choose move: prioritize reducing distance to target; avoid opponent; deterministic tie-break
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        key = (-d_t, d_o, -abs(dx) - abs(dy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return list(best if best is not None else (0, 0))