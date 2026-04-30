def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for (rx, ry) in resources:
        if (rx, ry) not in obst:
            res.append((rx, ry))
    deltas = [(-1, -1), (-1, 0), (-1, 1),
              (0, -1), (0, 0), (0, 1),
              (1, -1), (1, 0), (1, 1)]

    def risk(x, y):
        # stronger penalty if adjacent to obstacle
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obst:
                    r += 2.0
        # mild penalty for being "trapped" near edges with obstacles (proxy)
        if x == 0 or x == w - 1 or y == 0 or y == h - 1:
            r += 0.25
        return r

    best = (0, 0)
    best_v = -10**18

    # If no resources, just drift to safer central-ish cell while avoiding obstacles
    cx, cy = w // 2, h // 2

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        v = 0.0

        v -= 3.0 * risk(nx, ny)

        # Prefer closing on a resource we can reach sooner than opponent
        if res:
            best_here = -10**18
            for (rx, ry) in res:
                d_self = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # claim advantage: self closer than opponent is valuable
                claim = (d_opp - d_self)
                # also prefer resources in the direction we are moving (small tie-break)
                bias = -0.02 * (cheb(nx, ny, cx, cy))
                # If immediate pickup, huge
                pick = 40.0 if (nx == rx and ny == ry) else 0.0
                # Encourage stealing: if opponent is closer, penalize significantly
                score = pick + 6.0 * claim - 1.0 * d_self + 0.35 * (-abs(d_self - d_opp)) + bias
                if score > best_here:
                    best_here = score
            v += best_here
        else:
            v += -0.08 * cheb(nx, ny, cx, cy)

        # Avoid moving toward opponent too aggressively (helps prevent being "raced" for same resources)
        v -= 0.12 * cheb(nx, ny, ox, oy)

        # Deterministic tie-break: prefer smaller |dx|+|dy| then stable ordering
        if v > best_v + 1e-9:
            best_v = v; best = (dx, dy)
        elif abs(v - best_v) <= 1e-9:
            if (abs(dx) + abs(dy)) < (abs(best[0]) + abs(best[1])):
                best = (dx, dy)
    return [best[0], best[1]]