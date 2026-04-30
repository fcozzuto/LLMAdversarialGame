def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h
    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))
    best = None
    best_val = -10**18
    any_res = False
    for rx, ry in resources:
        if (rx, ry) not in obs:
            any_res = True
            break
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        if any_res:
            dmin = 10**18
            tie = 0
            for rx, ry in resources:
                if (rx, ry) in obs:
                    continue
                d = dist(nx, ny, rx, ry)
                if d < dmin:
                    dmin = d
                    tie = dist(ox, oy, rx, ry)
                elif d == dmin:
                    t2 = dist(ox, oy, rx, ry)
                    if t2 < tie:
                        tie = t2
            val = -dmin
            if tie < 10**18:
                val += 0.01 * (tie - dist(nx, ny, ox, oy))
        else:
            val = -dist(nx, ny, ox, oy)
        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best if best is not None else [0, 0]