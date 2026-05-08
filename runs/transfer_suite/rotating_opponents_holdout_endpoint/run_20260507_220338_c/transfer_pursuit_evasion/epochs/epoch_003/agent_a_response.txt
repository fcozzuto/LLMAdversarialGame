def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x0, y0 = map(int, observation.get("self_position", [0, 0]))
    xo, yo = map(int, observation.get("opponent_position", [0, 0]))
    turn = int(observation.get("turn_index", 0))
    self_role = str(observation.get("self_role", "")).lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    ox = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            ox.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def wall_dist(x, y):
        return min(x, w - 1 - x, y, h - 1 - y)

    best = None
    best_key = None
    parity = turn & 1

    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            continue
        ddx, ddy = x - xo, y - yo
        cheb = max(abs(ddx), abs(ddy))
        dman = abs(ddx) + abs(ddy)
        wd = wall_dist(x, y)
        step_par = (dx != 0) ^ (dy != 0)
        avoid_wall_pen = 0.35 * wd

        if pursuer:
            # Chase while keeping some separation from walls to avoid corner traps.
            score = - (8.0 * cheb + 1.0 * dman) + 0.15 * wd + (0.05 if parity == (step_par & 1) else 0.0)
        else:
            # Evasion: maximize distance, prefer staying away from walls, but still corner if tied.
            score = (8.5 * cheb + 1.2 * dman) + 0.10 * wd + avoid_wall_pen + (0.05 if parity == (step_par & 1) else 0.0)

        key = (score, wd, cheb if pursuer else -cheb, -dman if pursuer else dman, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]