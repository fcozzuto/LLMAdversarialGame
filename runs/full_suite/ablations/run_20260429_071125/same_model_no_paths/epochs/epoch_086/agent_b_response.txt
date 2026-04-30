def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    best = None
    best_key = None  # maximize advantage => minimize (-advantage)
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        adv = do - ds  # positive means we're closer
        key = (-adv, ds, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)

    tx, ty = best

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = cheb(nx, ny, tx, ty)
        opp_sep = cheb(nx, ny, ox, oy)
        move_key = (d_to_target, -opp_sep, dx, dy)
        if best_move_key is None or move_key < best_move_key:
            best_move_key = move_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]