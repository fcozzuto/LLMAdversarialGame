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

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_options(cx, cy):
        deltas = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    deltas.append((dx, dy, nx, ny))
        deltas.sort(key=lambda t: (abs(t[2]-ox)+abs(t[3]-oy), t[2], t[3]))
        return deltas

    if not res:
        # Drift to far corner from opponent (while favoring our x direction deterministically).
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0], c[1]))
        best_dx, best_dy = 0, 0
        best = 10**9
        for dx, dy, nx, ny in step_options(sx, sy):
            d = cheb(nx, ny, tx, ty)
            if d < best or (d == best and (nx, ny) < (sx + best_dx, sy + best_dy)):
                best = d
                best_dx, best_dy = dx, dy
        return [int(best_dx), int(best_dy)]

    # Choose target resource where we are relatively closer than opponent.
    best = None
    best_key = None
    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        key = (do - ds, -min(ds, do), x, y)  # prefer we win it; break deterministically
        if best_key is None or key > best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    # Greedy move toward target with tie-breaks; ensure no obstacle.
    cand = step_options(sx, sy)
    cand.sort(key=lambda t: (cheb(t[2], t[3], tx, ty), cheb(t[2], t[3], ox, oy), t[2], t[3]))
    return [int(cand[0][0]), int(cand[0][1])]