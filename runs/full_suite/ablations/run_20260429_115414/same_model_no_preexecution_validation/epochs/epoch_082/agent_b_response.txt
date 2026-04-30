def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_near(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        tx, ty = (w - 1, h - 1) if cheb(sx, sy, w - 1, h - 1) <= cheb(sx, sy, 0, 0) else (0, 0)
        best = (0, 0)
        bd = cheb(sx, sy, tx, ty)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if in_bounds(nx, ny):
                    d = cheb(nx, ny, tx, ty)
                    if d < bd:
                        bd = d
                        best = (dx, dy)
        return [best[0], best[1]]

    best_r = resources[0]
    best_adv = -10**9
    # Choose a resource where we are relatively closer than the opponent.
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) * 2 - obs_near(rx, ry)
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        d = cheb(nx, ny, rx, ry)
        # Prefer getting closer, avoid tight obstacle clusters, and avoid walking into opponent proximity too much.
        opp_prox = cheb(nx, ny, ox, oy)
        val = -d * 4 + (opp_prox) * 0.2 - obs_near(nx, ny) * 0.