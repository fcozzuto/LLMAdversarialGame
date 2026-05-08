def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur = (sx, sy)

    if unclaimed:
        candidates = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in unclaimed:
                dc = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
                # Prefer closer to center, farther from opponent, then deterministic
                candidates.append((0, dc, -do, nx, ny, dx, dy))
            else:
                candidates.append((1, 0, 0, nx, ny, dx, dy))
        if candidates:
            best = min(candidates)
            return [int(best[5]), int(best[6])]

    # Fallback: move toward center while avoiding obstacles; deterministic tie-break
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dist = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        do = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        key = (dist, -do, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    if best is not None:
        return [int(best[1]), int(best[2])]
    return [0, 0]