def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    x0, y0 = observation.get("self_position", [0, 0])
    xo, yo = observation.get("opponent_position", [0, 0])
    x0 = int(x0); y0 = int(y0); xo = int(xo); yo = int(yo)
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

    best_dxdy = [0, 0]
    best_score = None

    # For determinism: fixed tie-breaker by move ordering, plus slight turn-based bias.
    bias = 0.0001 * (turn & 1)

    for dx, dy in moves:
        x, y = x0 + dx, y0 + dy
        if not in_bounds(x, y) or (x, y) in ox:
            continue

        ddx = x - xo
        ddy = y - yo
        cheb = abs(ddx) if abs(ddx) > abs(ddy) else abs(ddy)
        dman = abs(ddx) + abs(ddy)
        wd = wall_dist(x, y)

        # Encourage avoiding walls to reduce getting cornered; stronger when evading.
        wall_pen = (0.9 if not pursuer else 0.45) * (w - 1 - wd) / max(1, w - 1)

        # Avoid stepping into "bad" shadow squares behind obstacles relative to opponent direction (lightweight).
        obs_shadow = 0.0
        stepx = 0 if ddx == 0 else (1 if ddx > 0 else -1)
        stepy = 0 if ddy == 0 else (1 if ddy > 0 else -1)
        for t in (1, 2):
            bx = x + t * stepx
            by = y + t * stepy
            if 0 <= bx < w and 0 <= by < h and (bx, by) in ox:
                obs_shadow = 0.15
                break

        if pursuer:
            # Minimize distance to opponent; keep some freedom from walls.
            score = - (7.5 * cheb + 1.2 * dman) - 1.4 * wall_pen - 2.0 * obs_shadow + bias * (dx == 0 and dy == 0)
        else:
            # Maximize distance from opponent while staying safe from walls/obstacles.
            score = (7.5 * cheb + 1.2 * dman) - 2.6 * wall_pen - 2.0 * obs_shadow + bias * (dx == 0 and dy == 0)

        if best_score is None or score > best_score:
            best_score = score
            best_dxdy = [dx, dy]

    return [int(best_dxdy[0]), int(best_dxdy[1])]