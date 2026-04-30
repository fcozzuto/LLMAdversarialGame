def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand.sort()  # deterministic tie-breaking

    # Choose resource that maximizes current advantage; then evaluate moves relative to it.
    best_res = None
    best_adv = -10**18
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = (do - ds) * 100 - ds
            if adv > best_adv:
                best_adv = adv
                best_res = (rx, ry)
    else:
        best_res = (w // 2, h // 2)

    rx, ry = best_res
    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        ds2 = cheb(nx, ny, rx, ry)
        do2 = cheb(ox, oy, rx, ry)

        # If moving reduces opponent's advantage even when we don't reach, prefer it.
        # Also small penalty for staying if a move exists.
        val = (do2 - ds2) * 100 - ds2 - (5 if (dx == 0 and dy == 0) else 0)

        # If we can potentially "race" multiple resources, add a small lookahead term.
        if len(resources) > 1:
            # Consider up to first 6 resources deterministically to keep cheap.
            for i in range(min(6, len(resources))):
                r2x, r2y = resources[i]
                dsx = cheb(nx, ny, r2x, r2y)
                dox = cheb(ox, oy, r2x, r2y)
                val += (dox - dsx) * 8

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]