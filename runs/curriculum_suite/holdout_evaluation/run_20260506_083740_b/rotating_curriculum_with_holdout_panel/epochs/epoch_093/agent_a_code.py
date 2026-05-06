def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not resources:
        # Anti-sweep positioning: match opponent row, keep safe.
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -abs(ny - oy) - 0.3 * abs(nx - ox)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        adv = -10**18
        for rx, ry in resources:
            self_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            # Favor resources where we're closer; slightly reduce opp advantage if too close.
            v = (opp_d - self_d) - 0.15 * self_d + 0.02 * (opp_d - self_d)
            if v > adv:
                adv = v
        # Anti-sweep bias: try to stay on/near opponent's row while advancing advantage.
        row_bias = -abs(ny - oy) - 0.25 * abs(nx - ox)
        vtot = 1.0 * adv + 0.18 * row_bias
        if vtot > bestv:
            bestv = vtot
            best = (dx, dy)
    return [best[0], best[1]]