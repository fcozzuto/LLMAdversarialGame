def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Choose target: maximize advantage; if none positive, minimize opponent distance; tie-break by closer to self then coords.
    best = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        adv = do - ds
        if best is None:
            best = (adv, -do, ds, tx, ty, tx, ty)
        else:
            cand = (adv, -do, ds, tx, ty, tx, ty)
            if cand > best:
                best = cand
    _, _, _, _, _, tx, ty = best

    # Move: pick best delta among 8-neighbors + stay that reduces distance to target; prefer safe move.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_ds = cheb(sx, sy, tx, ty)
    best_move = (None, None, None)  # (improvement, -opp_dist, dist_self, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        imp = cur_ds - nds
        cand = (imp, -do, nds, dx, dy)
        if best_move[0] is None or cand > best_move:
            best_move = cand
    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[3]), int(best_move[4])]