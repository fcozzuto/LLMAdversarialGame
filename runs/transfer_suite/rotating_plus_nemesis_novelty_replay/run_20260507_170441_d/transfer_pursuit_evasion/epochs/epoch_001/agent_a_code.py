def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    obstacles = observation.get("obstacles", [])
    self_role = observation.get("self_role", "")
    ox, oy = self_pos[0], self_pos[1]
    px, py = opp_pos[0], opp_pos[1]
    obs_set = {(p[0], p[1]) for p in obstacles if len(p) >= 2}
    cap_r = observation.get("capture_radius", 0)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    eps = 1e-9

    is_pursuer = ("pursuer" in self_role.lower()) or ("catch" in self_role.lower()) or ("chaser" in self_role.lower())
    # Distance squared (capture at exact same cell for r=0)
    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = ox + dx, oy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d2 = dist2(nx, ny, px, py)
        # capture check (radius 0 => exact match)
        if cap_r == 0:
            captured = (nx == px and ny == py)
        else:
            captured = dist2(nx, ny, px, py) <= cap_r * cap_r

        if is_pursuer:
            # Maximize: capture first, otherwise minimize distance to avoid giving evader room.
            score = 0.0
            if captured:
                score = 1e12
            else:
                score = 1e6 / (d2 + eps)
            # Add small preference for steering away from obstacles by penalizing proximity to them.
            # Since obstacles are few, this helps deterministically.
            prox_pen = 0
            for ax, ay in obs_set:
                dd2 = dist2(nx, ny, ax, ay)
                if dd2 <= 4:
                    prox_pen += (4 - dd2)
            score -= prox_pen * 10.0
            if best_score is None or score > best_score + 1e-12:
                best_score = score
                best = (dx, dy)
        else:
            # Evader: maximize distance; if would allow immediate capture, heavily avoid it.
            if captured:
                score = -1e12
            else:
                score = d2
                # Prefer staying near a corner far from pursuer to be hard to corner-cut.
                corner_candidates = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
                # Deterministic: choose best corner for current candidate
                best_corner_d2 = -1
                for cx, cy in corner_candidates:
                    dd2 = dist2(nx, ny, cx, cy)
                    if dd2 > best_corner_d2:
                        best_corner_d2 = dd2
                score += best_corner_d2 * 0.05
                # Avoid obstacles a bit
                prox_pen = 0
                for ax, ay in obs_set:
                    dd2 = dist2(nx, ny, ax, ay)
                    if dd2 <= 9:
                        prox_pen += (9 - dd2)
                score -= prox_pen * 2.0
            if best_score is None or score > best_score + 1e-12:
                best_score = score
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]