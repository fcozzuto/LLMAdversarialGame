def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources.sort()
    best_t = resources[0]
    best_adv = -10**18
    best_my = 10**9
    for tx, ty in resources:
        dm = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - dm  # want me closer than opponent
        if adv > best_adv or (adv == best_adv and (dm < best_my or (dm == best_my and (tx, ty) < best_t))):
            best_adv = adv
            best_my = dm
            best_t = (tx, ty)

    tx, ty = best_t
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv = opd - myd
        # small tie-breakers: approach my target, avoid staying if not needed
        val = adv * 1000 - myd * 2 - (1 if (dx == 0 and dy == 0) else 0)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    if best_move == (0, 0):
        # If target-adjacent blocked, choose any move that maximizes my improvement minus opponent's proximity to target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny):
                myd = cheb(nx, ny, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                val = (opd - myd) * 1000 - myd
                if val > best_val:
                    best_val = val
                    best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]