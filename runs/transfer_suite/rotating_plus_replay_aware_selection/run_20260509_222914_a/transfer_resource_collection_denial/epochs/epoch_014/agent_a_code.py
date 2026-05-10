def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        return [dx, dy]

    def cell_blocked(cx, cy):
        if cx < 0 or cx >= w or cy < 0 or cy >= h:
            return True
        return (cx, cy) in obstacles

    best = [0, 0]
    best_val = -10**18

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if cell_blocked(nx, ny):
            continue

        # Prefer moves that create (and keep) a distance advantage toward some resource,
        # while avoiding moving adjacent to obstacles too much.
        obs_pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    obs_pen += 1

        # For each resource, compute our margin after the move (higher is better).
        # Use max-over-resources to be opportunistic, but penalize low certainty by min distance.
        best_res = -10**18
        nearest = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = (opd - myd)  # positive means we are closer
            # Encourage quick capture and margin, discourage giving up targets.
            val = margin * 100 - myd + (margin >= 0) * 20
            if val > best_res:
                best_res = val
            if myd < nearest:
                nearest = myd

        val = best_res - obs_pen * 3 - nearest * 0.5
        if val > best_val:
            best_val = val
            best = [dx0, dy0]

    return best