def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}
    role = (observation.get("self_role") or "pursuer").lower()

    cands = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    nearest_corner_dist = min(man(ox, oy, cx, cy) for cx, cy in corners)

    def clearance(nx, ny):
        if not obs_set:
            return 4
        d = min(abs(nx - ax) + abs(ny - ay) for (ax, ay) in obs_set)
        return d if d < 6 else 6

    best_dx, best_dy = 0, 0
    best_score = None
    sign = 1.0 if role == "pursuer" else -1.0

    for dx, dy in cands:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            continue

        d_opp = man(nx, ny, ox, oy)
        # Corner pressure: anticipate evader trying to reach a corner; pursuer tries to cut off.
        opp_corner_after = nearest_corner_dist - min(
            man(ox, oy, cx, cy) - man(nx, ny, cx, cy) for cx, cy in corners
        ) / 4.0
        opp_corner_after = max(0.0, float(opp_corner_after))

        clr = clearance(nx, ny)
        # Penalize near obstacles; prefer staying away for stability.
        obst_pen = (6 - clr) * (0.7 if role == "pursuer" else 0.9)

        # Pursuer minimizes distance; evader maximizes distance (and keeps away from pursuer).
        # Also add a small deterministic bias toward diagonals to reach corners faster.
        diag_bias = 0.05 if (dx != 0 and dy != 0) else 0.0

        # For pursuer: additionally reduce distance to the corner that evader is closest to.
        if role == "pursuer":
            target_corner = min(corners, key=lambda c: man(ox, oy, c[0], c[1]))
            d_corner = man(nx, ny, target_corner[0], target_corner[1])
            score = (d_opp * 1.4) + (d_corner * 0.7) + obst_pen + diag_bias + (opp_corner_after * 0.1)
            key = -score  # maximize
        else:
            score = (d_opp * -1.2) - (man(nx, ny, sx, sy) * 0.1)  # push away from pursuer (it is sx,sy)
            score = (-score)  # simplify to positive maximize
            score = ( -man(nx, ny, ox, oy) * -1.0 ) + (-clr * 0.0) + obst_pen + (-d_opp) * (-0.1) + diag_bias
            key = sign * ((-d_opp) + (-nearest_corner_dist) * 0.05) - obst_pen * 0.1

        if best_score is None or key > best_score:
            best_score = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]