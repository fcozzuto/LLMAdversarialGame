def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def best_for_targets(tx, ty):
        best = None
        bx, by = sx, sy
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                sc = d
                if best is None or sc < best:
                    best = sc
                    bx, by = nx, ny
        if best is None:
            return 0, 0
        return bx - sx, by - sy

    if resources:
        target = resources[0]
        bd = abs(sx - target[0]) + abs(sy - target[1])
        for x, y in resources[1:]:
            d = abs(sx - x) + abs(sy - y)
            if d < bd:
                bd = d
                target = (x, y)
        return best_for_targets(target[0], target[1])

    dx, dy = best_for_targets(ox, oy)
    if dx in (-1, 0, 1) and dy in (-1, 0, 1):
        return [dx, dy]
    return [0, 0]