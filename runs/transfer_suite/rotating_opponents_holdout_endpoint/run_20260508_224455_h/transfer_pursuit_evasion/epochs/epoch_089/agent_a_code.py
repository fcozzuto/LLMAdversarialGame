def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x")), int(p.get("y"))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
        except Exception:
            pass

    role = str(observation.get("self_role") or "").lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    def score_candidate(nx, ny):
        base = dist2(nx, ny)
        boundary_pen = 0
        if not (0 <= nx < w and 0 <= ny < h):
            boundary_pen += 10**6
        if (nx, ny) in obs:
            boundary_pen += 10**6
        corner_bias = (nx in (0, w - 1)) + (ny in (0, h - 1))
        if is_evader:
            # Prefer moving away and into a corner away from pursuer.
            corner_dir = ((nx == (w - 1 if ox < sx else 0)) + (ny == (h - 1 if oy < sy else 0)))
            return (-base) + 0.3 * corner_bias + 0.6 * corner_dir + boundary_pen
        else:
            # Prefer moving toward; slightly bias toward corners (can help with cornering).
            toward_bonus = 0.2 * ((nx - sx) * (ox - sx) + (ny - sy) * (oy - sy))
            return base - 0.05 * corner_bias + boundary_pen + 0.01 * toward_bonus

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sc = score_candidate(nx, ny)
        if best_score is None:
            best_score = sc
            best_move = (dx, dy)
        else:
            if is_evader:
                if sc > best_score:
                    best_score, best_move = sc, (dx, dy)
            else:
                if sc < best_score:
                    best_score, best_move = sc, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]