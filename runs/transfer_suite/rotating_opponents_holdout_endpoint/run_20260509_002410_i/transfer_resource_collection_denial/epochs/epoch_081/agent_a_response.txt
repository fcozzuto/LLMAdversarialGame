def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best = None  # (priority, my_d, op_d, tx, ty)
    for r in resources:
        if not r or len(r) < 2:
            continue
        tx = int(r[0]); ty = int(r[1])
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obstacles:
            continue
        my_d = cheb(sx, sy, tx, ty)
        op_d = cheb(ox, oy, tx, ty)
        lead = my_d - op_d  # <=0 means we reach no later than opponent
        priority = 0 if lead <= 0 else 1
        cand = (priority, my_d, op_d, tx, ty)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    _, _, _, tx, ty = best

    moves = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    sx0, sy0 = sx, sy

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    primary = (dx, dy)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    order = [primary] + [m for m in moves if m != primary]
    for mx, my in order:
        nx, ny = sx0 + mx, sy0 + my
        if not valid(nx, ny):
            continue
        # Greedily minimize our distance, tie-break maximize opponent distance to target.
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox + (1 if ox < tx else -1 if ox > tx else 0), oy + (1 if oy < ty else -1 if oy > ty else 0), tx, ty)
        # The opponent "advance" above is only for deterministic tie-breaking; if it pushes out, still works fine.
        return [mx, my]

    return [0, 0]