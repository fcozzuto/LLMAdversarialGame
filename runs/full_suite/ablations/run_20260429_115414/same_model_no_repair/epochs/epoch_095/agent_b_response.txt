def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    candidates = []
    for rx, ry in resources:
        if (rx, ry) in blocked:
            continue
        if rx == sx and ry == sy:
            return [0, 0]
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Different from "be closer": first strongly contest resources that opponent is closer to.
        # Primary: maximize (od - myd). Secondary: if tied, minimize myd (finish fast).
        candidates.append((od - myd, -myd, rx, ry))
    if not candidates:
        return [0, 0]

    # Choose a single target deterministically.
    candidates.sort(reverse=True)
    _, _, tx, ty = candidates[0]

    # One-step lookahead: choose move that reduces our distance to target and
    # (slightly) increases opponent's distance to the same target.
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        od_now = cheb(ox, oy, tx, ty)
        # Use a proxy: after we move closer, we prefer not to also enable opponent to get closer in the same direction.
        # Since we don't know opponent's move, penalize moves that "open" lines by increasing distance from us to target less.
        # (proxy is deterministic and simple)
        move_score = (myd2, cheb(nx, ny, ox, oy), -od_now)
        if best is None or move_score < best:
            best = move_score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best is not None else [0, 0]