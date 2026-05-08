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
    unclaimed_set = set()
    for a in unclaimed:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = a[0], a[1]
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                unclaimed_set.add((int(x), int(y)))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if unclaimed_set:
            best = None
            for ux, uy in unclaimed_set:
                d1 = (nx - ux) * (nx - ux) + (ny - uy) * (ny - uy)
                if best is None or d1 < best:
                    best = d1
            d = best if best is not None else 999999
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        oppd = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        candidates.append((d, -oppd, ny, nx, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort()
    return [int(candidates[0][4]), int(candidates[0][5])]