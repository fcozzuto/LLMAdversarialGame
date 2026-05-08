def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ox, oy = observation.get("opponent_position", (sx, sy))
    ox, oy = int(ox), int(oy)

    def norm_points(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                try:
                    x, y = int(x), int(y)
                except:
                    continue
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = norm_points(observation.get("obstacles"))
    self_t = norm_points(observation.get("self_territory"))
    opp_t = norm_points(observation.get("opponent_territory"))
    unclaimed = norm_points(observation.get("unclaimed_cells"))
    resources = norm_points(observation.get("resources"))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, 0), (0, -1), (0, 0), (0, 1), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best = None
    best_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = 0
        if (nx, ny) in resources:
            sc += 1000 - (abs(nx - sx) + abs(ny - sy))
        if (nx, ny) in unclaimed:
            sc += 60
        if (nx, ny) in self_t:
            sc += 30
        if (nx, ny) in opp_t:
            sc += 90
        sc -= 2 * (abs(nx - ox) + abs(ny - oy))  # keep pressure toward opponent
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]