def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1, h - 1
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    bestv = -10**18
    opp_best_t = None
    for r in resources:
        t = cheb(ox, oy, r[0], r[1])
        if opp_best_t is None or t < opp_best_t:
            opp_best_t = t

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            ts = cheb(nx, ny, rx, ry)
            to = cheb(ox, oy, rx, ry)
            if ts < to:
                v += (to - ts) * 12 - ts
            elif ts > to:
                v -= (ts - to) * 10 + 2 * (ts - to)
            else:
                v -= 3
        # additional push to contest the resource opponent seems closest to
        if opp_best_t is not None:
            to_cells = []
            for rx, ry in resources:
                to = cheb(ox, oy, rx, ry)
                if to == opp_best_t:
                    to_cells.append((rx, ry))
            if to_cells:
                rx, ry = min(to_cells, key=lambda p: (cheb(nx, ny, p[0], p[1]), p[0], p[1]))
                v += 8 * (opp_best_t - cheb(nx, ny, rx, ry))
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]