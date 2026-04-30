def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best = None
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if resources:
            md = None
            for rx, ry in resources:
                d = (nx - rx) * (nx - rx) + (ny - ry) * (ny - ry)
                if md is None or d < md:
                    md = d
            val = (md, (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy), dx, dy)
        else:
            val = (((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)) * -1, -abs(nx - (w // 2)) - abs(ny - (h // 2)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]