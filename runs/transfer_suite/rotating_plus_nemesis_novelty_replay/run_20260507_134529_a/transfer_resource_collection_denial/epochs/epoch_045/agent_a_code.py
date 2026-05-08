def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obs
    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    if not resources:
        best = (-10**18, 0, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): nx, ny = sx, sy
            d = cheb(nx, ny, ox, oy)
            cand = (d, 0, nx, ny)
            if cand > best: best = cand
        return [best[2]-sx if best[2] != sx else 0, best[3]-sy if best[3] != sy else 0]

    best_move = None
    best_score = (-10**18, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny): nx, ny = sx, sy

        best_margin = -10**18
        best_ds = 10**9
        best_do = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive means we can be closer than opponent
            if margin > best_margin or (margin == best_margin and (ds < best_ds or (ds == best_ds and do < best_do))):
                best_margin, best_ds, best_do = margin, ds, do

        dist_opp = cheb(nx, ny, ox, oy)
        cand = (best_margin, -best_ds, dist_opp, -best_do)
        if cand > best_score:
            best_score = cand
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]