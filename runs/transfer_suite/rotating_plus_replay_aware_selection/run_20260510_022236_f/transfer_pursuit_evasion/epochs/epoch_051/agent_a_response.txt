def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    role = str(observation.get("self_role", "") or "").lower()
    is_evader = "evader" in role

    obstacles = observation.get("obstacles", []) or []
    obs = []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def clamp(x, y):
        if not in_bounds(x, y):
            return sx, sy
        return x, y

    # Deterministic tie-break: fixed move order in deltas.
    # Score uses distance change plus obstacle/wall penalties and corner bias.
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Corner bias for evader: move toward farthest corner from pursuer.
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: dist(c, (ox, oy)))
    near_corner = min(corners, key=lambda c: dist(c, (ox, oy)))

    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        d_cur = dist((sx, sy), (ox, oy))
        d_new = dist((nx, ny), (ox, oy))

        # Obstacle repulsion: prefer increasing distance from nearest obstacle.
        if obs:
            nearest = min(abs(nx - ax) + abs(ny - ay) for ax, ay in obs)
        else:
            nearest = 999

        wall_pen = 0
        # If move gets closer to wall in the evasion phase, allow; otherwise penalize only if extremely close.
        if nx in (0, w - 1) and ny in (0, h - 1):
            wall_pen = -1  # corners are usually fine; keep slight preference for corner routes

        if is_evader:
            # Evader wants to increase distance to opponent and drift toward far_corner.
            # Also avoid being too close to obstacles.
            corner_term = -dist((nx, ny), far_corner)
            prog = (d_new - d_cur)  # positive is good
            avoid = 0
            if nearest <= 1:
                avoid = -120
            elif nearest == 2:
                avoid = -35
            elif nearest <= 3:
                avoid = -10
            score = 6 * prog + corner_term + avoid + wall_pen
        else:
            # Pursuer wants to decrease distance and keep to near_corner from evader perspective.
            corner_term = -dist((nx, ny), near_corner)
            prog = (d_new - d_cur)  # negative is good
            avoid = 0
            if nearest <= 1:
                avoid = -140
            elif nearest == 2:
                avoid = -45
            elif nearest <= 3:
                avoid = -12
            score = -6 * prog + corner_term + avoid + wall_pen

        # Add a tiny deterministic preference to reduce oscillation: prefer moves that change position if tied.
        same_pos_bonus = 0 if (nx == sx and ny == sy) else 0.01
        score += same_pos_bonus

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move