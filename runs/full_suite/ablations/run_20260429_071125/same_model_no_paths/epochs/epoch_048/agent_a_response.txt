def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    res_set = set(resources)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best_target = None
        best_key = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (-(ds < do), -(do - ds), ds, cheb(tx, ty, 3, 3))
            if best_key is None or key > best_key:
                best_key = key
                best_target = (tx, ty)
        tx, ty = best_target
    else:
        tx, ty = 3, 3

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if (nx, ny) in res_set:
            score = 10**9
        else:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            d_opp_next = cheb(ox, oy, nx, ny)
            score = 2000 * (cheb(nx, ny, tx, ty) == 0)  # kept harmless; resources handled above
            score += (d_opp - d_self) * 100  # go where we are closer than opponent
            score += -d_self * 2               # keep pressure toward target
            score += -cheb(nx, ny, ox, oy) * 0.5  # mild spacing
            score += (d_opp_next > 0) * 0.1
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]