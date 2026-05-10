def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_r = None
    best_m = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles or not inb(rx, ry):
            continue
        m = man(sx, sy, rx, ry)
        if best_m is None or m < best_m:
            best_m = m
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resource: drift toward opponent to contest.
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    best_score = None
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        score = opd * 2 - myd - (1 if (dx, dy) == (0, 0) else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]