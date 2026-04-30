def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny): 
                continue
            v = (cheb(nx, ny, cx, cy), -cheb(nx, ny, ox, oy), dx, dy)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best if bestv is not None else [0, 0]

    # Choose a target where we currently have the biggest distance advantage (opp farther than us).
    best_t = None
    best_adv = None
    best_dist = None
    for tx, ty in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        adv = od - md
        cand = (adv, -md, tx, ty)
        if best_adv is None or cand > (best_adv, -best_dist, best_t[0], best_t[1] if best_t else -1):
            best_adv = adv
            best_dist = md
            best_t = (tx, ty)

    tx, ty = best_t
    # Step toward target but keep an eye on not letting opponent close the gap too quickly.
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        adv_after = opd - myd
        opp_to_me = cheb(ox, oy, nx, ny)
        # Prefer: larger advantage, then smaller my distance, then keep opponent farther.
        score = (-adv_after, myd, -opp_to_me, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move if best_score is not None else [0, 0]