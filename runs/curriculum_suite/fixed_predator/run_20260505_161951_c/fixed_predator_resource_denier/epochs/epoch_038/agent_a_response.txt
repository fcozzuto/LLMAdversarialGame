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
        best = (0, 0)
        bestv = -10**18
        # stay away from opponent and toward far corner
        tx, ty = w - 1, h - 1
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
    # evaluate move by its effect on taking a resource vs denying one closer to opponent
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue

        v = 0
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            if myd == 0:
                v += 20000
            # win potential: being closer than opponent matters most
            v += (opd - myd) * 120
            # deny potential: if opponent currently closer/tied, moving closer hurts them more
            v += 80 if (opd <= myd) else 0
            # small penalty for taking longer
            v -= myd * 8

        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]