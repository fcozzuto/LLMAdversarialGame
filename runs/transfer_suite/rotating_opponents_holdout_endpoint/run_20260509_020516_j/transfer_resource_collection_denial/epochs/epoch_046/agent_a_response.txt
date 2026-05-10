def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = (-10**9, 0, 0)
        for dx, dy, nx, ny in moves:
            d = cheb(nx, ny, ox, oy)
            if d > best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose move that maximizes advantage for taking some resource first (distance difference),
    # while discouraging giving the opponent a closer line and handling near-obstacle congestion.
    best_val = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in moves:
        my_block = 0
        # penalize stepping adjacent to obstacles (often slows in tight setups)
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                tx, ty = nx + ax, ny + ay
                if (tx, ty) in obstacles:
                    my_block += 1
        cur_val = -my_block * 0.05

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # If we can reach same resource significantly sooner, strongly prefer.
            adv = (opd - myd)
            # Small preference for nearer resources once advantage is comparable.
            clos = -myd * 0.01
            # If opponent is already at the resource, avoid (they will take it).
            take_risk = 0
            if cheb(ox, oy, rx, ry) == 0:
                take_risk = 50
            v = adv + clos - take_risk
            if v > cur_val:
                cur_val = v

        if cur_val > best_val or (cur_val == best_val and (dx, dy) < best_move):
            best_val = cur_val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]