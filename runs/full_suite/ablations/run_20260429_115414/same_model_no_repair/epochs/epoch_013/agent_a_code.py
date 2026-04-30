def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty, fromx, fromy):
        dx = 0 if tx == fromx else (1 if tx > fromx else -1)
        dy = 0 if ty == fromy else (1 if ty > fromy else -1)
        return fromx + dx, fromy + dy, dx, dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1, h - 1)
        if cheb(sx, sy, 0, 0) < cheb(sx, sy, w - 1, h - 1):
            tx, ty = 0, 0
        nx, ny, dx, dy = step_toward(tx, ty, sx, sy)
        if valid(nx, ny):
            return [dx, dy]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # prioritize (1) us not slower than opponent, (2) biggest lead, (3) smaller my distance
        lead = opd - myd
        faster = 1 if myd <= opd else 0
        # tie-break deterministically by coordinates
        key = (faster, lead, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    _, _, dx0, dy0 = step_toward(tx, ty, sx, sy)
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, tx, ty)
            # primary: reduce distance to target; secondary: avoid letting opponent get closer to same target
            opp_dist = cheb(ox, oy, tx, ty)
            candidates.append((dist, -(opp_dist - dist), nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [candidates[0][4], candidates[0][5]]