def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ax, ay = int(p[0]), int(p[1])
            if 0 <= ax < w and 0 <= ay < h:
                obs.add((ax, ay))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_target = None
    best_adv = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer or equal (win tie-break on path)
        if best_adv is None or adv > best_adv or (adv == best_adv and ds < cheb(sx, sy, best_target[0], best_target[1])):
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target

    def score_after(nx, ny):
        if (nx, ny) in obs:
            return -10**9
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Small preference for progress toward other resources if equally advantageous
        return (do - ds) * 1000 - ds

    best = [0, 0]
    best_sc = -10**9
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        sc = score_after(nx, ny)
        # deterministic tie-break: lexicographic move order
        if sc > best_sc or (sc == best_sc and (dxm, dym) < (best[0], best[1])):
            best_sc = sc
            best = [dxm, dym]

    return best