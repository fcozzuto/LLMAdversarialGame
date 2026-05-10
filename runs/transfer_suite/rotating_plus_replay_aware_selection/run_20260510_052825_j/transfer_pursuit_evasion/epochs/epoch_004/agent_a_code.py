def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(p[0], p[1]) for p in obstacles}

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()

    def is_pursuer(role):
        r = role.replace("-", "_")
        return ("purs" in r) or (r == "pursuer")

    def is_evader(role):
        r = role.replace("-", "_")
        return ("evad" in r) or (r == "evader")

    pursuer = is_pursuer(self_role) and not is_evader(self_role)
    if not pursuer and is_pursuer(opp_role) and not is_evader(opp_role):
        pursuer = False
    elif not pursuer and is_pursuer(opp_role) and is_evader(opp_role):
        pursuer = True
    elif pursuer and is_evader(self_role):
        pursuer = False

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: (c[0] - ox) * (c[0] - ox) + (c[1] - oy) * (c[1] - oy))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_d = None
    best = (0, 0)

    # Deterministic tie-breaker via ordered evaluation in deltas
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        d_opp = dist2(nx, ny, ox, oy)
        d_corner = dist2(nx, ny, far_corner[0], far_corner[1])
        # Add corner pressure to reduce circling when evading
        score = (d_opp - 0.05 * d_corner) if not pursuer else (-d_opp + 0.02 * d_corner)
        if best_d is None:
            best_d = score; best = (dx, dy)
        else:
            if score > best_d:
                best_d = score; best = (dx, dy)

    if best == (0, 0) and (sx, sy) in obs:
        return [0, 0]

    # If everything was blocked, fallback to staying
    return [best[0], best[1]]