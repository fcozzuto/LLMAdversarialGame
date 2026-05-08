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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if (sx, sy) in obstacles:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        tgt = min(resources, key=lambda r: (manhattan((sx, sy), r), r[1], r[0]))
        best = None
        best_val = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            d_t = manhattan((nx, ny), tgt)
            d_o = manhattan((nx, ny), (ox, oy))
            val = (d_t, -d_o, dy, dx)
            if best_val is None or val < best_val:
                best_val, best = val, (dx, dy)
        return list(best) if best is not None else [0, 0]

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d_o = manhattan((nx, ny), (ox, oy))
        val = (-d_o, dy, dx)
        if best_val is None or val < best_val:
            best_val, best = val, (dx, dy)
    return list(best) if best is not None else [0, 0]