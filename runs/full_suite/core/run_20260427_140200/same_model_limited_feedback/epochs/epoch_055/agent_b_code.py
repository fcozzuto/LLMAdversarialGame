def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev
    # Pick a contested target: closest to me, but penalize when opponent is closer.
    if resources:
        best_r = None
        best_val = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            val = myd + 0.75 * (myd - opd if myd > opd else 0.0) + 0.01 * (abs(rx - w/2) + abs(ry - h/2))
            if best_val is None or val < best_val:
                best_val, best_r = val, (rx, ry)
        tx, ty = best_r
    else:
        # No resources: go to a stable point near center, biased away from opponent.
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        if (nx, ny) in obs:
            continue
        # Prefer reducing distance to target; slight preference to keep away from opponent.
        my_next = dist((nx, ny), (tx, ty))
        if resources:
            opp_next = dist((ox, oy), (tx, ty))
            contest = 0.8 * (my_next - opp_next if my_next > opp_next else 0.0)
        else:
            contest = 0.0
        away = 0.02 * dist((nx, ny), (ox, oy))
        score = my_next + contest + away
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]