def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = observation.get("resources") or []
    resources = [tuple(r) for r in res if isinstance(r, (list, tuple)) and len(r) >= 2]
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < bestd or (d == bestd and (rx, ry) < target):
                bestd = d
                target = (rx, ry)

    best = None
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if target is not None:
            score = -man(nx, ny, target[0], target[1])
        else:
            score = man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best[0], best[1]]