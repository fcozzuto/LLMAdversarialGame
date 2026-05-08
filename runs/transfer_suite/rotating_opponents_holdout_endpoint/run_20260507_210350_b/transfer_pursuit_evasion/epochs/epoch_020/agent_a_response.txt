def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    role = str(observation.get("self_role", "")).lower()
    pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit"))

    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def nearest_obs_dist(nx, ny):
        if not obstacles:
            return 99
        md = 99
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d < md:
                md = d
        return md

    def corner_bias(nx, ny):
        # For pursuer: prefer central-ish blocking (farther from corners).
        # For evader: prefer corners to complicate pursuit.
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        best = 99
        for cx, cy in corners:
            d = cheb(nx, ny, cx, cy)
            if d < best:
                best = d
        return best  # smaller is closer to some corner

    best_move = [0, 0]
    best_val = None

    # Deterministic evaluation order: keep first max/min found
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = cheb(nx, ny, ox, oy)
        d_obs = nearest_obs_dist(nx, ny)

        # Obstacle penalty: strongly avoid moving adjacent to obstacles.
        # d_obs==0 won't happen (obstacle cell), but adjacent still matters.
        obs_pen = 0
        if d_obs <= 1:
            obs_pen = 50 - 10 * d_obs
        elif d_obs == 2:
            obs_pen = 8

        # Pursuer wants smaller distance; evader wants larger.
        # Also encourage reducing max(dx,dy) component-wise to keep pressure.
        ddx = abs(nx - ox)
        ddy = abs(ny - oy)
        squeeze = (ddx + ddy)

        val = 0
        if pursuer:
            val = -d_op * 10 - obs_pen - (squeeze * 0.1) - (corner_bias(nx, ny) * 0.05)
        else:
            val = d_op * 10 - obs_pen + (corner_bias(nx, ny) * 0.08) - (squeeze * 0.02)

        if best_val is None:
            best_val = val
            best_move = [dx, dy]
        else:
            if pursuer:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            else:
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]