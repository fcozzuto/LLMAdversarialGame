def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**9

    def cell_score(x, y):
        if not inb(x, y) or (x, y) in obstacles:
            return None
        if (x, y) in unclaimed:
            t = 12.0
        elif (x, y) in opp_terr:
            t = 10.0
        elif (x, y) in self_terr:
            t = 3.0
        else:
            t = 6.0
        dcen = abs(x - cx) + abs(y - cy)
        dopp = abs(x - ox) + abs(y - oy)
        adj = 0
        for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + ax, y + ay) in self_terr:
                adj += 1
        return t + 0.45 * (4 - dcen / 2.0) + 0.08 * adj - 0.02 * dops_safe(dopp)

    def dops_safe(d):
        return d

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = cell_score(nx, ny)
        if sc is None:
            continue
        if sc > best_score + 1e-9:
            best_score = sc
            best = (dx, dy)
        elif abs(sc - best_score) <= 1e-9 and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]