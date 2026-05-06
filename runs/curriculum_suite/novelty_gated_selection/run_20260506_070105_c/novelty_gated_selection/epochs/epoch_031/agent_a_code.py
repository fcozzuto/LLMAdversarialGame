def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", None) or []
    obstacles = observation.get("obstacles", None) or []
    remaining = observation.get("remaining_resource_count", None)

    obs = set()
    for p in obstacles:
        try:
            obs.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    tgt = None
    if resources and (remaining is None or int(remaining) > 0):
        bestd = 10**9
        besti = 10**9
        for i, r in enumerate(resources):
            try:
                rx, ry = int(r[0]), int(r[1])
            except Exception:
                continue
            d = man(sx, sy, rx, ry)
            if d < bestd or (d == bestd and i < besti):
                bestd, besti, tgt = d, i, (rx, ry)
    if tgt is None:
        tgt = (ox, oy)

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        if tgt == (ox, oy) and man(nx, ny, ox, oy) == 0:
            score = 0
        else:
            score = man(nx, ny, tgt[0], tgt[1])
            score = score * 100 + (man(nx, ny, ox, oy))  # prefer resources, then keep pressure
        if score < best_score or (score == best_score and (dx, dy) == best_move):
            best_score, best_move = score, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]