def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    self_role = (observation.get("self_role") or "").lower()
    is_pursuer = ("purs" in self_role) or ("chase" in self_role) or ("tag" in self_role)

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1,  0), (0,  0), (1,  0),
             (-1,  1), (0,  1), (1,  1)]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def dist2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    best = None
    best_val = None

    # Evader bias: farthest corner from opponent
    far_corner = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)

        if is_pursuer:
            # minimize distance to opponent; tie-break by moving more directly (dot-product sign)
            dot = dx * (ox - sx) + dy * (oy - sy)
            val = (-d_opp, -dot, -abs(nx - ox) - abs(ny - oy))
        else:
            # maximize distance to opponent; tie-break by moving toward farthest corner and away from opponent along the line
            corner_d = dist2(nx, ny, far_corner[0], far_corner[1])
            away_dot = dx * (sx - ox) + dy * (sy - oy)
            val = (d_opp, away_dot, -corner_d)

        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]