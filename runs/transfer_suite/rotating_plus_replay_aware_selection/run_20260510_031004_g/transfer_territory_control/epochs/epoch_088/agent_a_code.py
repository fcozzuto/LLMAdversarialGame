def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    obstacles = set(map(tuple, observation.get("obstacles", []) or []))
    self_terr = set(map(tuple, observation.get("self_territory", []) or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory", []) or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def score(x, y):
        if (x, y) in obstacles:
            return -10**9
        base = 0
        if (x, y) in unclaimed:
            base = 1000
        elif (x, y) in opp_terr:
            base = 700
        elif (x, y) in self_terr:
            base = 300
        else:
            base = 80
        dcen = abs(x - cx) + abs(y - cy)
        dcen_term = -5 * dcen
        dopp = abs(x - ox) + abs(y - oy)
        steal_term = -2 * dopp
        return base + dcen_term + steal_term

    best_dx, best_dy = 0, 0
    best = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = score(nx, ny)
        if v > best:
            best = v
            best_dx, best_dy = dx, dy
    return [int(best_dx), int(best_dy)]