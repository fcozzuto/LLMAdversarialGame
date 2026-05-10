def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    role = observation.get("self_role", "")
    # candidate deltas (deterministic order)
    deltas = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, -1], [1, -1], [-1, 1]]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def move_is_valid(nx, ny):
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    # Score function depends on role
    if "purs" in role.lower():
        # Pursuer: minimize squared distance to opponent; prefer moves that reduce dx/dy magnitude
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not move_is_valid(nx, ny):
                continue
            ddx = nx - ox
            ddy = ny - oy
            dist2 = ddx * ddx + ddy * ddy
            # tie-breakers: prefer smaller abs(dx_to_target) and then lexicographic by chosen delta order
            score = (-dist2, -abs(ddx) - abs(ddy))
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]
    else:
        # Evader: maximize squared distance to pursuer; bias toward farthest corner from pursuer
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        # Choose farthest corner deterministically
        far_corner = None
        far_d = None
        for cx, cy in corners:
            d2 = (sx - cx) ** 2 + (sy - cy) ** 2
            if far_d is None or d2 > far_d:
                far_d = d2
                far_corner = (cx, cy)
        tx, ty = far_corner
        best = None
        best_score = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not move_is_valid(nx, ny):
                continue
            ddx = nx - ox
            ddy = ny - oy
            dist2 = ddx * ddx + ddy * ddy
            # Additional bias: increase distance to chosen corner (staying away from it isn't always right),
            # instead bias toward moving generally toward the opposite side of pursuer
            corner_d2 = (nx - tx) ** 2 + (ny - ty) ** 2
            score = (dist2, corner_d2)
            if best is None or score > best_score:
                best_score = score
                best = [dx, dy]
        return best if best is not None else [0, 0]