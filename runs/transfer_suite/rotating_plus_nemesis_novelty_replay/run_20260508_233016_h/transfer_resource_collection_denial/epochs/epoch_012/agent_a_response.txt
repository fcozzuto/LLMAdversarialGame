def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]
    tr = observation.get("turns_remaining", 0)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b, c, d):
        # diagonal allowed: use Chebyshev
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        # Opportunistic interception: maximize (opp_time - self_time_after)
        score = 0
        for rx, ry in resources:
            t_self = dist(nx, ny, rx, ry)
            t_opp = dist(ox, oy, rx, ry)
            lead = t_opp - t_self  # positive means we can reach sooner
            # Encourage near-term grabs, and block opponent when it would arrive first.
            urgency = 0
            if lead > 0:
                urgency = 20 - t_self
            else:
                urgency = 10 + lead  # less is worse; still prefer reducing opponent lead
            # Light horizon bias to avoid dithering near end
            horizon = (tr - t_self)
            score += urgency * 10 + (horizon if horizon > 0 else -2)
        # Prefer moves that reduce immediate distance to the currently best resource by our timing
        # (deterministic tie-break)
        best_r = None
        best_cmp = None
        for rx, ry in resources:
            t_self0 = dist(sx, sy, rx, ry)
            t_opp = dist(ox, oy, rx, ry)
            cmpv = (t_self0 - t_opp, t_self0, rx, ry)
            if best_cmp is None or cmpv < best_cmp:
                best_cmp = cmpv
                best_r = (rx, ry)
        if best_r is not None:
            score += (100 - dist(nx, ny, best_r[0], best_r[1]))

        # Deterministic tie-break: fixed ordering already; use score only
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]