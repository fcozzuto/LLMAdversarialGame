def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose a target with my advantage; if none, go for closest.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means I'm closer
        score = -adv * 1000 - ds  # maximize adv, then minimize my distance
        if best is None or score > best[0]:
            best = (score, rx, ry, adv)
    _, tx, ty, adv = best

    # If I'm not advantaged anywhere, retarget to closest resource (common failure fix).
    if adv <= 0:
        ds_best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            if ds_best is None or ds < ds_best[0] or (ds == ds_best[0] and (rx, ry) < (ds_best[1], ds_best[2])):
                ds_best = (ds, rx, ry)
        tx, ty = ds_best[1], ds_best[2]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in deltas:
        nx = sx + dxm
        ny = sy + dym
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)
        # Prefer getting closer to target; also try to keep away from opponent slightly.
        val = -myd * 1000 + oppd * 3
        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move