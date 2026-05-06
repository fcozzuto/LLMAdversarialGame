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
        # move to maximize distance from opponent while staying away from obstacles
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            d_center = max(abs(nx - (w - 1) / 2), abs(ny - (h - 1) / 2))
            # prefer fleeing but don't go overly cornered
            v = d_opp * 1000 - d_center * 5
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Key change: pick move by best "reach advantage" against all resources (deny/secure),
    # not just tracking a single target.
    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # local safety: avoid stepping into immediate trap by penalizing adjacency to obstacles
        adj_obs = 0
        for ox2, oy2 in ((nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny-1), (nx-1, ny+1), (nx+1, ny+1)):
            if 0 <= ox2 < w and 0 <= oy2 < h and (ox2, oy2) in obs:
                adj_obs += 1

        score = 0
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd == 0 and od == 0:
                # contested but we're already there
                score += 20000
            elif sd <= od:
                # likely to secure before (or tie with denial)
                gap = od - sd
                score += 1200 * (gap + 1) - 25 * sd
            else:
                # denial attempt: increase opponent's effort by moving closer/farther relative
                # (small positive if we're far so opponent can't trivially take it from them)
                score += -60 * (sd - od) - 10 * sd

        # slight bias away from opponent so denier can't mirror efficiently
        score += cheb(nx, ny, ox, oy) * 2 - adj_obs * 25

        if score > bestv or (score == bestv and (dx, dy) < best):
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]]