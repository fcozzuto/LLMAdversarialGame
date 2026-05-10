def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((int(x), int(y)) for x, y in obstacles)

    res = []
    for x, y in resources:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x, y, a, b):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def adj_obs_pen(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                nx, ny = x + ax, y + ay
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obs:
                    p += 1
        return p

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        my_pen = adj_obs_pen(nx, ny)
        cell_best = -10**18

        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            my_t = cheb(nx, ny, rx, ry)
            opp_t = cheb(ox, oy, rx, ry)
            # Prefer grabbing before opponent; if tie, prefer shorter self distance
            gap = opp_t - my_t
            v = gap * 100 - my_t * 2 - my_pen * 5
            # Slightly prefer resources closer to opponent only if we can beat them (gap positive)
            if gap > 0:
                d_opp = cheb(ox, oy, rx, ry)
                v += 3 - d_opp * 0.1
            cell_best = v if v > cell_best else cell_best

        # Small deterministic tie-break: prefer moves that reduce distance to nearest favorable resource
        if cell_best > best:
            best = cell_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]