def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

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

    def interior(x, y):
        d = x
        if w - 1 - x < d:
            d = w - 1 - x
        if y < d:
            d = y
        if h - 1 - y < d:
            d = h - 1 - y
        return d  # bigger means more interior

    if not resources:
        return [0, 0]

    best = None  # (score, ix, iy, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Strategy: pick move that most improves our chance to reach an available resource first,
        # while biasing toward interior (opponent patrol tends to stay near edges).
        if not resources:
            score = interior(nx, ny)
        else:
            score = -10**18
            # Evaluate best resource matchup for us on this move
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                d_me = cheb(nx, ny, rx, ry)
                d_opp = cheb(ox, oy, rx, ry)
                # Prefer resources we can reach earlier; small additional preference for being closer.
                val = (d_opp - d_me) * 100 - d_me + interior(nx, ny)
                if val > score:
                    score = val
            # Additional mild penalty if we are moving onto edge while opponent can likely contest
            edge_pen = 0
            if nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1:
                edge_pen = 5
            score -= edge_pen

        cand = (score, interior(nx, ny), -(abs(nx - ox) + abs(ny - oy)), dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[3], best[4]]