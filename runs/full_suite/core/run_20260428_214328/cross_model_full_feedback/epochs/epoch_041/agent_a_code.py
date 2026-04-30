def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if p is not None and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def legal_moves():
        lm = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in obst:
                lm.append((dx, dy, nx, ny))
        return lm

    legal = legal_moves()
    if not legal:
        return [0, 0]

    if not res:
        # deterministic chase with slight tie-break away from being stuck
        best = None; bestv = None
        for dx, dy, nx, ny in legal:
            v = -cheb(nx, ny, ox, oy) - 0.001 * (nx + ny)
            if bestv is None or v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Contest target: prefer resources we can reach earlier than opponent by a margin
    best_r = None; best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (myd - opd, myd, rx, ry)  # smaller is better on first, then tie breaks
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r

    # Score moves: approach target, avoid helping opponent too much, and keep distance from their immediate cell
    best = None; bestv = None
    for dx, dy, nx, ny in legal:
        myd = cheb(nx, ny, rx, ry)
        tgt = -myd
        # pressure: discourage moves that reduce opponent's distance to the same target
        opd_now = cheb(ox, oy, rx, ry)
        opd_next = cheb(ox, oy, rx, ry)  # opponent movement unknown; use conservative proxy: prefer larger opponent-target distance overall
        opp_proxy = opd_next  # constant but keeps structure stable
        # also avoid giving opponent a very close position to us (minimize our distance to opponent next)
        pressure = cheb(nx, ny, ox, oy)
        # tiny deterministic tie-break
        tie = -0.0005 * (nx * 31 + ny * 17)
        v = tgt - 0.02 * pressure + tie - 0.001 * opp_proxy
        if bestv is None or v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]