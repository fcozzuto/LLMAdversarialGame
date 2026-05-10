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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs

    def dist2(x, y):
        dx = x - ox
        dy = y - oy
        return dx * dx + dy * dy

    role = str(observation.get("self_role") or "").lower()
    evader = ("evader" in role) and ("pursuer" not in role)
    # If evader: maximize distance; else (pursuer): minimize distance.
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = dist2(nx, ny)
        # Small bias toward staying near center to reduce oscillation deterministically.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = -((nx - cx) ** 2 + (ny - cy) ** 2) * 0.001
        score = d + center_bias if evader else -d + center_bias
        if best_score is None or (score > best_score) or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return list(best) if best is not None else [0, 0]