def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    for dx, dy, nx, ny in valid:
        if (nx, ny) in res_set:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            dme = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            reach_diff = do - dme  # positive => I can reach earlier
            # "sweep" favor: resources closer to my current side of opponent's row
            sweep_bonus = -abs(ry - oy) * 0.05 + (dme == 0) * 0.0
            # tie-break deterministic: prefer shorter my distance if reach equal
            key = (reach_diff + sweep_bonus, -dme, -(rx + 7 * ry))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)

        tx, ty = best
        candidates = []
        for dx, dy, nx, ny in valid:
            if inb(nx, ny):
                d = cheb(nx, ny, tx, ty)
                # also discourage stepping into opponent-preferred cells by comparing distances from opponent
                opp_d = cheb(ox, oy, tx, ty)
                my_gain = (cheb(nx, ny, tx, ty) - cheb(sx, sy, tx, ty))  # negative is better
                candidates.append((my_gain, d, -opp_d, dx, dy))
        candidates.sort()
        dx, dy = candidates[0][3], candidates[0][4]
        return [int(dx), int(dy)]

    # No resources: drift to center while avoiding obstacles
    cx, cy = w // 2, h // 2
    best = None
    for dx, dy, nx, ny in valid:
        d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        key = (d, dx, dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    return best[1]