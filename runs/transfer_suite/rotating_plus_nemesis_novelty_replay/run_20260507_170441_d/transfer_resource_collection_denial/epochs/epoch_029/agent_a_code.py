def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Heuristic: prefer resources we can reach no later than opponent; otherwise prefer resources
    # that opponent is unlikely to reach soon (denier diversion), while still reducing distance to good options.
    best_val = -10**18
    best = [0, 0]

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            if selfd <= oppd:
                # Winning/contesting line: prioritize earlier and larger lead.
                gain = 1000 - 12 * selfd + 10 * (oppd - selfd)
            else:
                # Losing line: avoid deniable targets by favoring those with large opponent distance.
                gain = 2 * oppd - 8 * selfd - 6 * (selfd - oppd)
            # Combine with a slight preference for remaining closeness to any good pickup.
            v = max(v, gain)
        # Add a small stabilizer: move that reduces our distance to the best current target.
        # (Computed deterministically using current pos to avoid oscillations.)
        cur_best = 10**18
        for rx, ry in resources:
            cur_best = min(cur_best, cheb(sx, sy, rx, ry))
        v -= 0.1 * cheb(nx, ny, resources[0][0], resources[0][1])
        if v > best_val or (v == best_val and [dx, dy] == [0, 0] and best != [0, 0]):
            best_val = v
            best = [dx, dy]

    return best