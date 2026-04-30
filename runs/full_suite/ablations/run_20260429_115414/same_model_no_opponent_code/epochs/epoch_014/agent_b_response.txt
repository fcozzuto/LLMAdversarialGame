def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

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

    resources = observation.get("resources") or []
    res = [(int(p[0]), int(p[1])) for p in resources]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not res:
        best = None
        for dx, dy, nx, ny in valid:
            d = cheb(nx, ny, ox, oy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose a resource we can contest: maximize (opp_dist - self_dist), tie-break by smaller self_dist, then lexicographic.
    best_r = None
    best_gain = -10**9
    best_ds = 10**9
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gain = do - ds
        if gain > best_gain or (gain == best_gain and (ds < best_ds or (ds == best_ds and (rx, ry) < best_r))):
            best_gain = gain
            best_ds = ds
            best_r = (rx, ry)

    rx, ry = best_r

    # Step toward target; secondary objective: keep away from opponent when not improving target distance.
    best = None
    for dx, dy, nx, ny in valid:
        d1 = cheb(nx, ny, rx, ry)
        d2 = cheb(nx, ny, ox, oy)
        # Primary: minimize target distance; Secondary: maximize distance to opponent (i.e., minimize -d2).
        key = (d1, -d2, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]