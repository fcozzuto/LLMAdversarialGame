def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
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
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def obs_rep(x, y):
        pen = 0
        for (bx, by) in obstacles:
            adx = x - bx
            if adx < 0: adx = -adx
            ady = y - by
            if ady < 0: ady = -ady
            d = adx if adx > ady else ady
            if d == 0:
                return 10**6
            if d == 1:
                pen += 4
            elif d == 2:
                pen += 1
        return pen

    # Pick the resource that maximizes our competitive advantage, not just closeness.
    best_r = None
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Strong preference for states where we are already closer than opponent.
        adv = (od - sd) * 100 - sd * 3 - od
        # Mild tie-break to avoid going into crowded obstacle regions.
        adv -= obs_rep(rx, ry)
        if adv > best_val:
            best_val = adv
            best_r = (rx, ry)

    rx, ry = best_r

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        new_sd = cheb(nx, ny, rx, ry)
        new_od = cheb(ox, oy, rx, ry)
        # Move to reduce our distance, while keeping distance from opponent to avoid direct contests.
        score = (best_val // 100)  # keep scale stable/deterministic
        score += (new_od - new_sd) * 10
        score += -new_sd * 2
        score += cheb(nx, ny, ox, oy) * 0.5
        score -= obs_rep(nx, ny)
        if score > best_score: