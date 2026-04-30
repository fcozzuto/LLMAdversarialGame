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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resset = set(resources)
    if (sx, sy) in resset:
        return [0, 0]

    # Choose a target resource: maximize our "advantage"; if we are behind, pick the least-bad to intercept.
    best_t = None
    best_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = myd - opd  # smaller is better; we maximize negative adv by maximizing -adv
        score = -adv
        # slight tie-breaker: prefer closer overall (both)
        score -= 0.02 * (myd + opd)
        if score > best_adv:
            best_adv = score
            best_t = (rx, ry)
    tx, ty = best_t

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def obs_cost(x, y):
        if (x, y) in obstacles:
            return 10_000
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return 50 * c

    # Score each move by improving our distance to target while limiting opponent's progress to same target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        my_before = cheb(sx, sy, tx, ty)
        my_after = cheb(nx, ny, tx, ty)
        # Opponent hypothetical next move towards target (best-case for them).
        opp_best = 10**9
        for odx, ody in dirs:
            px, py = ox + odx, oy + ody
            if px < 0 or px >= w or py < 0 or py >= h:
                continue
            if (px, py)