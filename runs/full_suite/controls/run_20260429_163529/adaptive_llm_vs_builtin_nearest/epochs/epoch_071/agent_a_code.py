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

    res = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    bestv = None
    ti = int(observation.get("turn_index", 0) or 0)

    for x, y in res:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds  # positive means we are closer than opponent
        # Prefer advantage, then closer target, then farther from opponent; add tiny deterministic tie-breaker.
        v = adv * 1000 - ds * 10 + do + ((x * 31 + y * 17 + ti) % 7) * 0.001
        if best is None or v > bestv or (v == bestv and (do > cheb(ox, oy, best[0], best[1]))):
            bestv = v
            best = (x, y)

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestd = None
    bestmove = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        if bestd is None or d < bestd:
            bestd = d
            bestmove = (dx, dy)
        elif d == bestd:
            # Deterministic tie-break: prefer diagonal progress; then smaller remaining dx/dy gaps; then coordinate-based.
            sxg = abs(nx - tx) + abs(ny - ty)
            bdx, bdy = bestmove
            bx, by = sx + bdx, sy + bdy
            bsg = abs(bx - tx) + abs(by - ty)
            if sxg < bsg or (sxg == bsg and ((dx * 9 + dy * 7 + ti) % 13) < ((bdx * 9 + bdy * 7 + ti) % 13)):
                bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]