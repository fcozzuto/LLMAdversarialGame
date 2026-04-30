def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def val(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return None
        return True

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        target = resources[0]
        best = None
        for rx, ry in resources:
            d_self = dist((sx, sy), (rx, ry))
            d_opp = dist((ox, oy), (rx, ry))
            # Prefer resources closer than opponent (bigger advantage), then closer overall.
            score = (d_opp - d_self, -d_self)
            if best is None or score > best[0]:
                best = (score, rx, ry)
        tx, ty = best[1], best[2]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if val(nx, ny) is None:
            continue
        # Greedy toward target; small anti-collision with opponent.
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        score = (-d_t, d_o)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]