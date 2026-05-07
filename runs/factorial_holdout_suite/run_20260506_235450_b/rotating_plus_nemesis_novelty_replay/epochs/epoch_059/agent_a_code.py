def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    oxp, oyp = observation.get("opponent_position", (None, None))
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, 0), (0, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    best = None
    bestv = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Greedy: go to nearest resource; if none, go toward center.
        if resources:
            dmin = None
            for rx, ry in resources:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if dmin is None or d < dmin:
                    dmin = d
            v = dmin
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            v = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)

        # Small bias: if opponent exists, prefer moves that increase distance.
        if isinstance(oxp, int) and isinstance(oyp, int):
            v = (v, -((nx - oxp) * (nx - oxp) + (ny - oyp) * (ny - oyp)))

        if bestv is None or v < bestv:
            bestv = v
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]