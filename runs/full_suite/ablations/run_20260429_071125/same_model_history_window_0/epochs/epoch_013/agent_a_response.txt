def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]
    w, h = observation["grid_width"], observation["grid_height"]

    def in_bounds(a, b):
        return 0 <= a < w and 0 <= b < h

    def blocked(a, b):
        return (a, b) in obstacles

    def dist(a, b, c, d):
        return max(abs(a - c), abs(b - d))

    # Pick a resource that we can "claim" better than the opponent.
    best_res = None
    best_val = None
    for rx, ry in resources:
        if blocked(rx, ry):
            continue
        sd = dist(x, y, rx, ry)
        od = dist(ox, oy, rx, ry)
        val = sd - 0.85 * od  # lower is better
        if best_val is None or val < best_val:
            best_val = val
            best_res = (rx, ry)

    tx, ty = best_res if best_res is not None else (w // 2, h // 2)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_opp_d = dist(x, y, ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        my_d = dist(nx, ny, tx, ty)
        opp_d = dist(nx, ny, ox, oy)
        # Encourage approaching target, discouraging being too close to opponent,
        # and slight preference for increasing separation when contested.
        score = my_d * 1.8 - opp_d * (1.1 if best_res is not None else 0.7)
        if best_res is not None:
            sd0 = dist(x, y, tx, ty)
            od0 = dist(ox, oy, tx, ty)
            contested = 1.0 if sd0 <= od0 else 0.0
            score -= contested * (opp_d - cur_opp_d) * 0.9
        # Deterministic tie-break: smaller dx, then smaller dy.
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]