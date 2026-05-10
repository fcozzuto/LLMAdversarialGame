def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def center_bias(x, y):
        cx = (w - 1) / 2.0
        cy = (h - 1) / 2.0
        return -(abs(x - cx) + abs(y - cy))

    # Target: maximize (opponent advantage - my disadvantage), then prefer closers and centrality
    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # If ties, go for closer to me, then central, then higher coordinate sum
        key = (opd - myd, -myd, center_bias(rx, ry), -(rx + ry))
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Move choice: greedy improvement toward target, with safety from opponent and obstacle avoidance
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_to = cheb(nx, ny, tx, ty)
        my_from = cheb(sx, sy, tx, ty)
        opp_to = cheb(ox, oy, nx, ny)

        # Prefer getting strictly closer to target; otherwise tolerate if it improves safety
        progress = my_from - my_to

        # Safety: encourage staying away from opponent (strongly), but don't ignore progress
        safety = opp_to

        # Tie-break: prefer central cells slightly and lexicographically lower moves via ordering of deltas
        val = (progress, safety, center_bias(nx, ny), -(nx + ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move