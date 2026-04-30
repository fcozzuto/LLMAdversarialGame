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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_pos(nx, ny):
        # Higher is better
        best = -10**9
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent
            base = (d_op - d_me) * 10 - d_me
            # If opponent is already closer, discourage
            if d_op < d_me:
                base -= (d_me - d_op) * 8
            # Small bias toward central-ish lanes (break ties deterministically)
            base -= abs(rx - (w - 1) / 2.0) * 0.1 + abs(ry - (h - 1) / 2.0) * 0.1
            # Very slight preference for staying closer to resources cluster
            base += (1.0 / (1 + d_me))
            if base > best:
                best = base
        # Obstacle proximity deterrent
        adj = 0
        for ix in (-1, 0, 1):
            for iy in (-1, 0, 1):
                if ix == 0 and iy == 0:
                    continue
                if (nx + ix, ny + iy) in obstacles:
                    adj += 1
        return best - adj * 0.5

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = score_pos(nx, ny)
        # Deterministic tie-break: prefer (0,0), then smaller dx, then smaller dy
        if v > best_val or (v == best_val and (dx != 0 or dy != 0)):
            best_val = v
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]