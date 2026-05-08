def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def near_obs_pen(x, y):
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if (nx, ny) in obs:
                    pen += 2
        if (x, y) in obs:
            pen += 1000
        return pen

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources visible, drift to center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            val = cheb(nx, ny, cx, cy) + 0.4 * near_obs_pen(nx, ny)
            if best is None or val < best:
                best = val
                bestmv = [dx, dy]
        return bestmv if best is not None else [0, 0]

    # Resource race: prefer resources that are close to us and relatively far from opponent.
    bestmv, bestval = [0, 0], None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_pos_pen = near_obs_pen(nx, ny)
        best_resource = None
        # Evaluate best target from this next position
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # To counter resource_denier, strongly prefer targets opponent is unlikely to reach soon.
            # Small tie-break on absolute distance to secure collection.
            val = my_d - 1.25 * op_d
            if best_resource is None or val < best_resource:
                best_resource = val
        # Also avoid getting too close to opponent (helps vs denier contests).
        opp_close = 0
        d_to_opp = cheb(nx, ny, ox, oy)
        if d_to_opp <= 1:
            opp_close = 3.5
        total = best_resource + 0.35 * my_pos_pen + opp_close + 0.01 * d_to_opp
        if bestval is None or total < bestval:
            bestval = total
            bestmv = [dx, dy]
    return bestmv