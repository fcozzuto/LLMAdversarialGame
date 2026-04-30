def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        tx = (w - 1) if sx < ox else 0
        ty = (h - 1) if sy < oy else 0
        best = (0, (0, 0))
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            sc = -d
            if sc > best[0]:
                best = (sc, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose the resource that gives the biggest current advantage (opponent farther than us).
    best_target = None
    best_adv = -10**9
    for (rx, ry) in resources:
        du = cheb(sx, sy, rx, ry)
        dv = cheb(ox, oy, rx, ry)
        adv = dv - du
        # Slight tie-break: prefer closer overall to secure faster pickup.
        adv = adv * 10 - du
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    rx, ry = best_target
    # Greedy step toward target, but also keep/improve advantage vs opponent.
    best_move = (0, (0, 0))
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        du2 = cheb(nx, ny, rx, ry)
        dv2 = cheb(ox, oy, rx, ry)
        sc = (dv2 - du2) * 10 - du2
        # If we can match the target, slightly prefer ending closer to the line between them.
        midx = (sx + ox) // 2
        midy = (sy + oy) // 2
        sc -= cheb(nx, ny, midx, midy) // 2
        if sc > best_move[0]:
            best_move = (sc, (dx, dy))

    return [best_move[1][0], best_move[1][1]]