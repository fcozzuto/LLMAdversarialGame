def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x0, y0 = observation.get("self_position", [0, 0])
    xo, yo = observation.get("opponent_position", [0, 0])
    x0 = int(x0); y0 = int(y0); xo = int(xo); yo = int(yo)
    turn = int(observation.get("turn_index", 0))
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    obstacles = observation.get("obstacles", []) or []
    ox = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ox.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    def score_move(dx, dy):
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            return None
        ddx = x - xo
        ddy = y - yo
        cheb = abs(ddx) if abs(ddx) > abs(ddy) else abs(ddy)
        dman = abs(ddx) + abs(ddy)
        wd = wall_dist(x, y)
        center = min(wd, 3)  # cap influence
        # small deterministic bias to break ties
        bias = (dx * 3 + dy * 5 + turn) * 1e-6

        if is_pursuer:
            # Prefer getting closer; avoid walls to not be cornered through obstacles.
            return (-cheb) * 10.0 + (-dman) * 1.0 + center * 0.6 + bias
        else:
            # Evader: maximize distance and keep away from walls (evasion_corner).
            return (cheb) * 10.0 + (dman) * 1.0 + center * 0.8 + bias

    best = None
    best_sd = None
    for dx, dy in moves:
        sd = score_move(dx, dy)
        if sd is None:
            continue
        if best is None or sd > best:
            best = sd
            best_sd = [dx, dy]

    return best_sd if best_sd is not None else [0, 0]