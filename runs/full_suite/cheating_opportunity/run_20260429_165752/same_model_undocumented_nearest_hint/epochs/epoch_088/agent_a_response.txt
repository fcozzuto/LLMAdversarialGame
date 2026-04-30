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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = (0, 0)
        bestd = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if bestd is None or d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    best_move = (0, 0)
    best_val = None
    center = ((W - 1) // 2, (H - 1) // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        my_best = 10**9
        opp_best = 10**9
        best_adv = -10**9

        for tx, ty in resources:
            dm = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            if dm < my_best: my_best = dm
            if do < opp_best: opp_best = do
            adv = do - dm  # positive means we are closer than opponent to that resource
            if adv > best_adv: best_adv = adv

        # Prefer moves that: maximize advantage, then minimize our distance,
        # then slightly prefer moving toward center when tied.
        val = (best_adv, -my_best, -(cheb(nx, ny, center[0], center[1])), -(abs(dx) + abs(dy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]