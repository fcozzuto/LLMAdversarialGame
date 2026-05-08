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

    best = None
    best_val = None
    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            continue
        ddx, ddy = x - xo, y - yo
        cheb = abs(ddx) if abs(ddx) > abs(ddy) else abs(ddy)
        man = abs(ddx) + abs(ddy)
        wd = wall_dist(x, y)
        # Pursuer: minimize distance; avoid walls to reduce wall-run evasion. Evader: maximize distance; also avoid edges.
        if is_pursuer:
            val = (cheb, -wd, man, dx * 0.1 + dy * 0.05 + (turn % 7) * 1e-4)
            better = best_val is None or val < best_val
        else:
            val = (-cheb, -man, -wd, dx * 0.1 + dy * 0.05 + (turn % 7) * 1e-4)
            better = best_val is None or val < best_val
        if better:
            best_val = val
            best = [dx, dy]

    return best if best is not None else [0, 0]