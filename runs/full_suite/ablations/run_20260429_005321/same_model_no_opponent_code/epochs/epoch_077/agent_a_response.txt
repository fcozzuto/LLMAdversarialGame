def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [w - 1, h - 1]))

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    R = set(resources)

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if (sx, sy) in R:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        # fallback: run away from opponent towards farthest corner
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        target = (tx, ty)
    else:
        # choose resource: closest to us; among ties, farthest from opponent
        best = None
        for r in resources:
            ds = cheb(sx, sy, r[0], r[1])
            do = cheb(ox, oy, r[0], r[1])
            # If opponent is much closer, reduce priority
            opp_closeness = 3 if do <= ds else 0
            key = (ds + opp_closeness, -do, r[0], r[1])
            if best is None or key < best[0]:
                best = (key, r)
        target = best[1]

    # pick move: minimize distance to target; tie-break maximize distance from opponent
    best_move = None
    best_key = None
    tx, ty = target
    for dx, dy, nx, ny in valid:
        ds = cheb(nx, ny, tx, ty)
        do = cheb(nx, ny, ox, oy)
        # slight preference to not step onto adjacent opponent if equally good
        adj_pen = 1 if cheb(nx, ny, ox, oy) <= 1 else 0
        key = (ds, -(do - adj_pen), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]