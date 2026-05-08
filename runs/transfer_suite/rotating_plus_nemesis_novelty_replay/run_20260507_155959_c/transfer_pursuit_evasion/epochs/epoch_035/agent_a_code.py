def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    self_role = str(observation.get("self_role", "")).lower()
    is_pursuer = ("pursur" in self_role) or (self_role == "pursuer")

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj_obs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def clear_move(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def obstacle_penalty(x, y):
        p = 0
        for dx, dy in adj_obs:
            if (x + dx, y + dy) in obstacles:
                p += 3
        if (x, y) in obstacles:
            p += 1000
        return p

    best_move = cand[0]
    best_val = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not clear_move(nx, ny):
            continue

        d = abs(nx - ox) + abs(ny - oy)
        step_cost = (abs(dx) + abs(dy)) * 0.05
        pen = obstacle_penalty(nx, ny)

        if is_pursuer:
            # Prefer closing distance while not running into walls/obstacles.
            val = (-d * 100) - (pen * 5) - step_cost
            # Small preference to move along the strongest axis toward the opponent.
            if nx != ox: val += -abs(1 if nx > ox else -1) * 0.01
            if ny != oy: val += -abs(1 if ny > oy else -1) * 0.01
        else:
            # Prefer running away and toward open space.
            val = (d * 100) - (pen * 8) - step_cost
            # If distance ties, bias toward the farthest corner from opponent.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
            val += (abs(far_corner[0] - nx) + abs(far_corner[1] - ny)) * 0.5

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]