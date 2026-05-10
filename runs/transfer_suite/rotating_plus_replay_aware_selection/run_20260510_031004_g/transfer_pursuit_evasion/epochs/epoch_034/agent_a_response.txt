def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role", "") or "").lower()
    evader = ("evader" in role) or ("runner" in role) or ("escape" in role) or (("pursuer" not in role) and ("chaser" not in role))

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

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]

    best_dxdy = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs_set:
            nx, ny = sx, sy

        d_opp = dist2(nx, ny, ox, oy)

        obs_pen = 0
        for ax in (nx - 1, nx, nx + 1):
            for ay in (ny - 1, ny, ny + 1):
                if (ax, ay) in obs_set:
                    obs_pen += 1

        corner_bonus = 0
        if evader:
            # Prefer being far from opponent and deep into the most distant corner.
            corner_bonus = max(dist2(nx, ny, cx, cy) for (cx, cy) in corners) * 0.002

        # Boundary mobility: evader likes to avoid being boxed in; pursuer likes to advance.
        near_edge = (nx == 0) or (nx == w - 1) or (ny == 0) or (ny == h - 1)
        edge_term = -0.15 if (evader and near_edge) else (0.02 if (not evader and near_edge) else 0.0)

        val = d_opp + corner_bonus + edge_term - obs_pen * 0.35
        if not evader:
            val = -val  # pursuer minimizes distance, so flip

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_dxdy[0], best_dxdy[1])):
            best_val = val
            best_dxdy = [dx, dy]

    return best_dxdy