def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def clamp_in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    # Pick a target based on "who can reach it first" advantage, with tie-break on being closer.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = manh(sx, sy, rx, ry)
        opd = manh(ox, oy, rx, ry)
        key = (opd - myd, -myd, -(rx + ry))  # maximize opponent gap, then minimize my distance
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)
    if best_r is None:
        # all resources blocked
        return [0, 0]

    tx, ty = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        myd = manh(nx, ny, tx, ty)
        opd = manh(ox, oy, tx, ty)

        # 1-step lookahead: prefer increasing lead, then reduce own distance.
        # Also slightly discourage stepping toward opponent to avoid being intercepted.
        lead = opd - myd
        opp_dist_now = manh(nx, ny, ox, oy)
        opp_dist_curr = manh(sx, sy, ox, oy)
        opp_pen = 0.2 * (opp_dist_curr - opp_dist_now)  # penalty if we get closer

        val = (lead, -myd, opp_dist_now - opp_pen)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]