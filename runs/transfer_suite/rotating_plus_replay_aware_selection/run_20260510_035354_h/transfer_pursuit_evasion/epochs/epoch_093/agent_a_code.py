def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    sr = str(observation.get("self_role") or "")
    pr = str(observation.get("opponent_role") or "")
    me_is_pursuer = ("purs" in sr.lower()) or ("evad" in pr.lower() and "purs" not in sr.lower())

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        d = dist(nx, ny, ox, oy)
        if me_is_pursuer:
            # Prefer smaller distance; tie-break by preferring moves that reduce Manhattan too.
            v = (-d, -abs(nx - ox) - abs(ny - oy))
        else:
            # Prefer larger distance.
            v = (d, abs(nx - ox) + abs(ny - oy))
        if best is None or v > bestv:
            best, bestv = (dx, dy), v

    return [int(best[0]), int(best[1])]