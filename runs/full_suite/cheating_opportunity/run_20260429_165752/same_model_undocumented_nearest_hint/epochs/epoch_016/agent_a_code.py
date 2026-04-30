def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def mobility(x, y):
        c = 0
        for ddx, ddy in dirs:
            nx, ny = x + ddx, y + ddy
            if legal(nx, ny):
                c += 1
        return c

    if resources:
        # Choose best target relative to opponent; prefer resources where we're closer.
        best = None
        best_val = -10**18
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # ds smaller => good; do smaller => bad; also prefer nearer overall.
            val = (do - ds) * 1000 - ds
            if val > best_val:
                best_val = val
                best = (tx, ty)
        tx, ty = best
    else:
        # No visible resources: drift toward center while avoiding obstacles.
        tx, ty = W // 2, H // 2

    best_move = (0, 0)
    best_score = -10**18
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # If we get significantly closer than opponent, heavily reward.
        opp_d = cheb(ox, oy, tx, ty)
        closer_gap = opp_d - d
        # Prefer higher mobility to avoid trapping against obstacles.
        score = -d * 3 + mobility(nx, ny) * 2 + closer_gap * 1.5
        # Deterministic tie-break: earlier dirs preferred.
        if score > best_score:
            best_score = score
            best_move = (ddx, ddy)

    return [best_move[0], best_move[1]]