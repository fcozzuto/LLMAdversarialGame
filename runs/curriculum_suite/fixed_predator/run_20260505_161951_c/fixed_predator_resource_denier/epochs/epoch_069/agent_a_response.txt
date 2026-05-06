def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
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
        best = (0, 0); bestv = -10**18
        tx, ty = w - 1, h - 1
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Main: aim to secure a resource first; otherwise deny the closest winning one.
    best = (0, 0); bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        v = 0
        for rx, ry in resources:
            ts = cheb(nx, ny, rx, ry)
            to = cheb(ox, oy, rx, ry)
            if ts < to:
                v += (to - ts) * 2000 - ts * 3
            elif ts == to:
                v += 500 - ts * 2
                if rx == nx and ry == ny:
                    v += 5000
            else:
                v -= (ts - to) * 40
        # small bias: prefer moving toward the most "contested" resource
        # (minimize (ts-to) gap for the best we can deny)
        best_gap = 10**9
        for rx, ry in resources:
            ts = cheb(nx, ny, rx, ry)
            to = cheb(ox, oy, rx, ry)
            gap = ts - to
            if gap < best_gap:
                best_gap = gap
        v -= best_gap * 5
        if v > bestv:
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]