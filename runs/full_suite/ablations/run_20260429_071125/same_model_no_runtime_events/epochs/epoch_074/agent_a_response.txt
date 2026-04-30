def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_adj(x, y):
        c = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (x + ix, y + iy) in obstacles:
                    c += 1
        return c

    resources.sort()
    best_r = None
    best_key = None
    # New policy: deny resources we can't reach first by prioritizing opponent distance
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        # tie-breakers: prefer closer, then fewer obstacle adjacencies (clearer routes)
        key = (-adv, ds, obst_adj(rx, ry), rx, ry) if adv <= 0 else (-1, -adv, ds, obst_adj(rx, ry), rx, ry)
        # Normalize keys without randomness: compare tuple directly
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If we are already on a resource, hold position to avoid walking away
    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Choose move that decreases our distance most; if tied, disrupt opponent more.
    best_move = None
    best_val = None
    for dx, dy, nx, ny in moves:
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        d_opp_next = cheb(nx, ny, rx, ry)  # proxy of our move doesn't affect opponent; use opponent-to-next heuristic below
        # better: maximize opponent distance to target by moving toward lines that increase their effective path:
        d_opp_pos = cheb(ox, oy, nx, ny)
        # Score combines: we want smaller d_self, also avoid giving opponent a shortcut by increasing their distance to us
        score = (d_self, -d_opp_pos, obst_adj(nx, ny), dx, dy)
        if best_val is None or score < best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]