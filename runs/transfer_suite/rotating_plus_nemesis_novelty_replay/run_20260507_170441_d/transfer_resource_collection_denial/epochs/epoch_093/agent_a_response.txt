def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((p[0], p[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def dist8(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        # Deny: move to reduce distance to opponent "front" corner while staying safe
        tx = 0 if ox > (w - 1) / 2 else (w - 1)
        ty = 0 if oy > (h - 1) / 2 else (h - 1)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -dist8(nx, ny, tx, ty)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose a target that we can reach at least as fast as opponent; otherwise choose most swingy
    best_t = None
    best_tv = -10**18
    for rx, ry in resources:
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        # primary: advantage (opp - self), secondary: closer overall
        advantage = od - sd
        # if we are significantly behind, penalize a lot
        behind_pen = 0
        if sd > od + 1:
            behind_pen = (sd - (od + 1)) * 4
        val = advantage * 10 - sd - behind_pen
        if val > best_tv or (val == best_tv and (rx, ry) < (best_t[0], best_t[1]) if best_t else False):
            best_tv = val
            best_t = (rx, ry)

    rx, ry = best_t
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Greedy toward target, but discourage moving away from being first
        sd_n = dist8(nx, ny, rx, ry)
        od_t = dist8(ox, oy, rx, ry)
        swing = (od_t - sd_n) * 10
        v = swing - sd_n
        # discourage dithering if target can be collected now
        if (nx, ny) == (rx, ry):
            v += 10000
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]