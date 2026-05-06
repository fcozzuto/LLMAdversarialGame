def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = (0, 0); best_s = -10**18

    resset = set(tuple(p) for p in resources)
    aligned_row = (sy == oy)  # counter potential row-sweeping by changing row when aligned

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if (nx, ny) in resset:
            return [dx, dy]

        base = 0
        myd_best = 10**9
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cur_my = cheb(sx, sy, rx, ry)
            myd_best = myd if myd < myd_best else myd_best
            base += (opd - myd) * 30 + (cur_my - myd) * 10 - myd

        # If aligned with opponent row, strongly prefer changing our row (hard to deny in-sweep).
        penalty = 0
        if aligned_row:
            penalty += 18 if ny == oy else 0
            penalty += 8 if ny in (oy-1, oy+1) else 0

        # Also discourage stepping adjacent to opponent.
        adj = cheb(nx, ny, ox, oy)
        penalty += 25 if adj <= 1 else 0

        s = base - penalty
        if s > best_s:
            best_s = s; best = (dx, dy)

    return [best[0], best[1]]