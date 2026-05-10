def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0: dx = -dx
        dy = y2 - y1
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources_sorted = sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))

    def cell_value(x, y):
        if (x, y) in obst:
            return -10**9
        best = -10**9
        for rx, ry in resources_sorted:
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 3.0 if (x, y) == (rx, ry) else 0.0
            lead = (do - ds)  # positive if we are closer (or opponent farther)
            deny = 0.08 * cheb(x, y, ox, oy)
            val = cap + 2.2 * lead - 0.35 * ds + deny
            if val > best:
                best = val
        # Gentle preference for staying away from obstacles (deterministic, local)
        adj = 0
        for nx in (-1, 0, 1):
            for ny in (-1, 0, 1):
                if nx == 0 and ny == 0:
                    continue
                ax, ay = x + nx, y + ny
                if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obst:
                    adj += 1
        return best - 0.25 * adj

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h:
            v = cell_value(nx, ny)
            # tie-break: prefer moves that reduce distance to the best target deterministically
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
    return best_move