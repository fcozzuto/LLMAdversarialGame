def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best = (0, 0, -10**18)

    if not resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Value: prefer resources where we are closer than opponent; otherwise choose moves that reduce that gap.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): nx, ny = sx, sy

        best_r = None
        best_val = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            margin = od - sd  # positive -> we are closer (denier-friendly contest)
            # Encourage immediate collection and winning contests.
            val = (margin * 1000) - sd
            if best_r is None or val > best_val:
                best_r = (rx, ry, sd, od, margin)
                best_val = val

        # If no good contest (margin <= 0), still avoid being too close to opponent to reduce contest hijacking.
        margin = best_r[4]
        opp_dist = cheb(nx, ny, ox, oy)
        v = best_val + (0 if margin > 0 else opp_dist * 5)
        if v > best[2]:
            best = (dx, dy, v)

    return [best[0], best[1]]