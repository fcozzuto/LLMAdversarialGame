def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def dsq(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        return dx*dx + dy*dy

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    cx0 = (w - 1) / 2.0; cy0 = (h - 1) / 2.0

    best_move = [0, 0]
    best_val = 10**30

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Choose the resource that best advances our winning chances (we prefer resources
        # where opponent is farther; if tied, we prefer closer/central).
        mv_val = 10**30
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            dself = dsq(nx, ny, rx, ry)
            dobj = dsq(ox, oy, rx, ry)

            # Lower is better. If we are behind (dself>dobj), penalize strongly.
            # Also penalize being far even when not behind.
            central = abs(rx - cx0) + abs(ry - cy0)
            val = (dself - dobj) * 10 + dself + 0.1 * central
            if val < mv_val:
                mv_val = val

        # Mild tie-break: prefer moves that reduce distance to our best target directly.
        if mv_val < best_val:
            best_val = mv_val
            best_move = [dx, dy]

    return best_move if isinstance(best_move, list) else [0, 0]