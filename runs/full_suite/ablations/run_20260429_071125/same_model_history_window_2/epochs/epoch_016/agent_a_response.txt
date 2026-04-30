def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) == 2:
            obstacles.add((p[0], p[1]))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def edge_pen(x, y):
        return (1 if x == 0 else 0) + (1 if x == w - 1 else 0) + (1 if y == 0 else 0) + (1 if y == h - 1 else 0)

    # Choose target resource: prefer where we are relatively closer (and especially where we can beat opponent soon).
    tx, ty = sx, sy
    if resources:
        best = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Primary: maximize "advantage" (opponent farther); Secondary: smaller my distance; Tertiary: deterministic tie-break.
            adv = opd - myd
            key = (adv, -myd, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    # One-step evaluation: move closer to target; avoid helping opponent by moving toward them; avoid getting cornered.
    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Closer to target is good.
        d_to_t = cheb(nx, ny, tx, ty)
        cur_to_t = cheb(sx, sy, tx, ty)

        # Distance to opponent: keep away (small penalty for proximity).
        d_to_o = cheb(nx, ny, ox, oy)
        cur_d_to_o = cheb(sx, sy, ox, oy)

        # Local collision risk proxy: discourage moving into cells adjacent to obstacles too much (proxy for congestion).
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    adj_obs += 1

        # If we're picking up a resource at (nx, ny), strongly prefer it.
        on_resource = 1 if (nx, ny) in set((r[0], r[1]) for r in resources) else 0

        # Score: encourage pickup, then improvement toward target, then separation from opponent, then reduce edge and congestion.
        score = 0
        score += 1000 * on_resource
        score += 30 * (cur_to_t - d_to_t)           # improve closeness
        score += 6 * (d_to_o - cur_d_to_o)         # keep distance
        score += 1.0 * d_to_o                       # even if equal improvement, prefer more distant
        score -= 0.4 * edge_pen(nx, ny)
        score -= 0.2 * adj_obs

        # Deterministic tie-break: lexicographically smallest move among equal scores.
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]