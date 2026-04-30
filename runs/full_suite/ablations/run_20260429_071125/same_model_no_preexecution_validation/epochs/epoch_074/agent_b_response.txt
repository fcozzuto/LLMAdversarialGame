def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a if a > b else b

    def adj_obs_count(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    if not resources:
        # No resources visible: move to maximize distance from opponent while avoiding obstacles
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d - 2 * adj_obs_count(nx, ny)
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    best_target = None
    best_key = None
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        if not valid(rx, ry):
            continue
        dm = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prioritize resources we can reach sooner than opponent, then closeness, then safety from opponent
        key = (do - dm, -dm, -(rx + ry))
        if best_key is None or key > best_key:
            best_key, best_target = key, (rx, ry)

    tx, ty = best_target
    # Evaluate immediate moves with a multi-term deterministic heuristic
    best, bestv = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(nx, ny, ox, oy)
        dm_cur = cheb(sx, sy, tx, ty)
        # Encourage progress vs not being just a short-step away from opponent capture
        progress = dm_cur - d_me
        # Mildly prefer moving away from opponent unless progress is strong
        v = 4 * progress + 0.6 * (d_op - cheb(sx, sy, ox, oy)) - 1.2 * adj_obs_count(nx, ny)
        # If we can step onto the target, strongly prefer it
        if nx == tx and ny == ty:
            v += 1000
        # If opponent is closer to the target than we are, prefer increasing separation
        if cheb(ox, oy, tx, ty) < cheb(sx, sy, tx, ty):
            v += 1.8 * (d_op)
        if v > bestv:
            bestv, best = v, (dx, dy)
    return [int(best[0]), int(best[1])]