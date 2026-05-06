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

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inside(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            dres = 10**9
            for r in resources:
                d = abs(nx - r[0]) + abs(ny - r[1])
                if d < dres:
                    dres = d
                    if dres == 0:
                        break
            dov = abs(nx - ox) + abs(ny - oy)
            val = (-dres * 10) + (dov)  # prioritize resource, keep away from opponent
            if val > best_val:
                best_val = val
                best = (dx, dy)
        if best is not None:
            return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dcenter = abs(nx - cx) + abs(ny - cy)
        dov = abs(nx - ox) + abs(ny - oy)
        val = (-dcenter * 2) + dov
        if val > best_val:
            best_val = val
            best = (dx, dy)
    if best is not None:
        return [best[0], best[1]]
    return [0, 0]