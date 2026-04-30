def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick target resource: prioritize where we're closer than opponent.
    best = None
    best_gap = -10**9
    best_ds = 10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        gap = do - ds
        if gap > best_gap or (gap == best_gap and ds < best_ds):
            best_gap, best_ds, best = gap, ds, (rx, ry)

    if best is None:
        # Fallback: just drift toward opponent's side while avoiding obstacles.
        tx, ty = (w - 1, h - 1)
    else:
        tx, ty = best

    # Score next moves: prefer resources, then reduce distance to target, then keep away from opponent.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        res_here = 1 if (nx, ny) in resources else 0
        ds = cheb(nx, ny, tx, ty)
        my_to_opp = cheb(nx, ny, ox, oy)
        # Encourage getting to target fast; discourage giving opponent too easy access.
        score = res_here * 1000 - ds * 10 + my_to_opp * 0.1
        # If our chosen target is "contested" (opponent closer), slightly boost moves that worsen their access.
        if best is not None:
            do_at_target = cheb(ox, oy, tx, ty)
            ds_at_self = cheb(sx, sy, tx, ty)
            if do_at_target <= ds_at_self:
                score += (my_to_opp <= cheb(nx, ny, ox, oy)) * 0  # keep deterministic no-op
                score -= cheb(ox, oy, tx, ty) * 0.01
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]