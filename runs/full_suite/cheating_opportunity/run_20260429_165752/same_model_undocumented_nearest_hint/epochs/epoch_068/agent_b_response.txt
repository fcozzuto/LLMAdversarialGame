def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**9

    # If no resources visible, move toward center to reduce worst-case distance.
    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            val = -d
            if val > best_val:
                best_val, best_move = val, (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose move that maximizes "advantage" toward the best resource.
    # Advantage = (opponent distance - our distance) after moving, with tie-break to reach sooner.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        move_best = -10**9
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            adv = do - ds  # positive means we are closer than opponent would be
            # Encourage finishing sooner and slightly prefer breaking ties toward nearest resources.
            val = adv * 100 - ds
            if val > move_best:
                move_best = val
        if move_best > best_val:
            best_val, best_move = move_best, (dx, dy)

    return [best_move[0], best_move[1]]