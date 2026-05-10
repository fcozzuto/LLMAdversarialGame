def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    pursuer = ("pursuer" in role) or ("chaser" in role) or ("hunter" in role)
    evader = not pursuer

    obs_set = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist2(x, y, a, b):
        dx, dy = x - a, y - b
        return dx * dx + dy * dy

    d0 = dist2(sx, sy, ox, oy)
    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    target_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy)) if evader else \
                     min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy
        d = dist2(nx, ny, ox, oy)

        # Primary objective: move toward/away from opponent.
        if pursuer:
            score = -d
        else:
            score = d

        # Secondary objective: for evader, bias toward farthest corner; for pursuer, toward nearest corner.
        tc = dist2(nx, ny, target_corner[0], target_corner[1])
        score += (-tc if evader else tc) * 0.001

        # Tertiary: prefer not to stall if it hurts the primary objective.
        stall_pen = 0.0
        if dx == 0 and dy == 0:
            stall_pen = -0.01 if ((pursuer and d > d0) or (evader and d < d0)) else -0.001
        score += stall_pen

        if best_val is None or score > best_val:
            best_val = score
            best = [dx, dy]

    dx, dy = best
    return [int(dx), int(dy)]