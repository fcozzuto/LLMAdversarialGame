def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Evaluate next-state best target, using deterministic scoring that prioritizes resources we can secure sooner.
    def move_score(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        best = -10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                val = 10**6 + (opd == 0) * -10  # strongly prefer collecting
            else:
                # We want to be significantly closer than opponent.
                # Also slightly prefer nearer resources to reduce time-to-collection.
                val = (opd - myd) * 100 - myd
                if opd < myd:
                    val -= 250  # discourage chasing resources opponent is closer to
            if val > best:
                best = val
        return best

    best_move = (0, 0)
    best_val = -10**9
    # Tie-break deterministically by preferring smallest dx, then dy.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        v = move_score(nx, ny)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]