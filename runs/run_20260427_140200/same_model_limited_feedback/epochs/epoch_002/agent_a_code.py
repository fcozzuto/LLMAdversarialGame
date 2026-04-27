def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs_set = set((p[0], p[1]) for p in obstacles)
    opp = (ox, oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs_set:
                continue
            # prefer moving away from opponent while drifting to center
            score = d((nx, ny), opp) - 0.001 * (abs(nx - cx) + abs(ny - cy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[1]), int(best[2])]

    # Strategic change: target resources where we are comparatively closer than opponent
    # Evaluate each candidate by the best "self advantage" it can achieve next.
    best_score = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        if (nx, ny) == opp:
            continue
        # minimize the most favorable "advantage gap" (self_dist - opp_dist)
        best_gap = None
        for rx, ry in resources:
            gap = d((nx, ny), (rx, ry)) - d(opp, (rx, ry))
            if best_gap is None or gap < best_gap:
                best_gap = gap
        if best_gap is None:
            continue
        # tie-break deterministically: prefer closer to opponent if gap is equal (pressure), else prefer larger opponent distance
        score = -best_gap + 0.0001 * d((nx, ny), opp)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]