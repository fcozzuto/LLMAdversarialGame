def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation["obstacles"]))
    resources = list(map(tuple, observation["resources"]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def best_target():
        if not resources:
            # If nothing to collect, drift toward opponent to contest.
            return (ox, oy)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            lead = opd - myd
            # Prefer resources where we are closer than opponent; then closer generally.
            cand = (-lead, myd, rx, ry)  # minimize
            if best is None or cand < best:
                best = cand
        if best is None:
            return (ox, oy)
        return (best[2], best[3])

    tx, ty = best_target()

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        lead = opd - myd  # bigger is better (we reduce our distance)
        # Tie-breaks: avoid wasting steps; also discourage moving away from opponent when tied.
        opp_dist = dist((nx, ny), (ox, oy))
        score = (0 - lead, myd, opp_dist, dx, dy)  # minimize
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]