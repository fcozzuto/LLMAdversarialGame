def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or [0, 0]
    ox, oy = observation.get("opponent_position") or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in role) or ("pursue" in role) or ("chaser" in role) or ("pursuit" in role)

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def clamp_score_obstacle_risk(x, y):
        # More risk near obstacles (tends to get trapped)
        risk = 0
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obs:
                risk += 1
        return risk

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    # Deterministic targeting for evader: prefer corners farthest from pursuer, but obstacle-aware via distance-after-move.
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_to_opp = dist(nx, ny, ox, oy)

        if pursuer:
            # Chase: minimize Manhattan distance; avoid obstacles by validity; slight preference to reduce opponent escape options.
            # Escape-option proxy: count free neighbor cells from the move.
            free_nbrs = 0
            for ddx, ddy in deltas[:-1]:
                tx, ty = nx + ddx, ny + ddy
                if valid(tx, ty):
                    free_nbrs += 1
            score = (-d_to_opp * 100) + free_nbrs  # lower distance dominates
        else:
            # Evade: maximize distance; additionally bias toward farthest corner target.
            target = max(corners, key=lambda c: dist(c[0], c[1], ox, oy))
            d_to_target = dist(nx, ny, target[0], target[1])
            risk = clamp_score_obstacle_risk(nx, ny)
            score = (d_to_opp * 100) + (d_to_target * 2) - (risk * 10)

        if best is None or score > best:
            best = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]