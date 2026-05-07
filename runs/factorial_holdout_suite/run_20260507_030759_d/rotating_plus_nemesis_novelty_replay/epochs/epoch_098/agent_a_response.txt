def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Target selection: prioritize resources we can reach no later than opponent,
    # otherwise maximize (opponent_dist - my_dist), then minimize my_dist.
    best = None
    best_key = None
    for rx, ry in res:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        can_own = myd <= opd
        adv = opd - myd  # higher is better
        # Deterministic tie-break by coordinates
        key = (1 if can_own else 0, adv, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    curd = cheb(sx, sy, tx, ty)

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer moves that reduce distance; if equal, prefer staying closer to opponent-blocking by using max my progress.
        mkey = (-1 if nd < curd else 0, -(nd - curd), -nd, dx, dy)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]