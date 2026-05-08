def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    unclaimed = observation.get("unclaimed_cells", []) or []
    if not unclaimed:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    unp = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            unp.append((int(c[0]), int(c[1])))
    if not unp:
        return [0, 0]

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        min_u = 10**18
        for ux, uy in unp:
            dd = (nx - ux) * (nx - ux) + (ny - uy) * (ny - uy)
            if dd < min_u:
                min_u = dd
        dist_o = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (min_u, -dist_o, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]