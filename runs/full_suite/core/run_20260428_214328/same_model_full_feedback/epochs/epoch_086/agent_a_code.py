def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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

    def best_towards(tx, ty, prefer_safe=True):
        bx = sx
        by = sy
        best = 10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
                if prefer_safe and d == 0 and (nx, ny) in obstacles:
                    continue
                score = d * 10 - (1 if dx == 0 and dy == 0 else 0)
                if score < best:
                    best = score
                    bx, by = nx, ny
        return bx, by

    target = None
    if resources:
        best = 10**18
        for x, y in resources:
            d = (x - sx) * (x - sx) + (y - sy) * (y - sy)
            if d < best:
                best = d
                target = (x, y)

    if target is not None:
        nx, ny = best_towards(target[0], target[1])
        return [nx - sx, ny - sy]

    nx, ny = best_towards(ox, oy, prefer_safe=False)
    return [nx - sx, ny - sy]