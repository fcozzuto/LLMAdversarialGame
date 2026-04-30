def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick a target that we can reach no slower than opponent if possible; otherwise pick the best available.
    best_t = None
    best_rank = None
    for tx, ty in resources:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # rank: prioritize ds <= do, then smaller ds, then smaller absolute coordinate tie-breaker
        rank = (0 if ds <= do else 1, ds, abs(tx - sx) + abs(ty - sy), tx, ty)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_t = (tx, ty)

    tx, ty = best_t
    want_close = True  # close to target unless opponent is about to intercept
    ds0 = cheb(sx, sy, tx, ty)
    do0 = cheb(ox, oy, tx, ty)

    # Move evaluation: contest/denial by increasing opponent distance to target when they are closer,
    # otherwise just reduce our distance to target. Also keep away from obstacles implicitly via validity.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = cheb(nx, ny, tx, ty)
        # How much we "deny" opponent: increase their distance when they are leading.
        do = cheb(ox, oy, tx, ty)  # opponent position unchanged this turn
        # Heuristic penalties/bonuses
        val = 0
        if do0 < ds0:
            # opponent is leading us on this target: try to delay by moving in a way that pushes us (and often forces paths)
            # toward a competing approach while increasing separation from opponent.
            val += (ds0 - ds) * 8
            val += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * 3
            val += (do - cheb(nx, ny, tx, ty)) * 2  # small bias to not overcommit
        else:
            val += (ds0 - ds) * 10
            val += (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)) * (2 if want_close else -2)

        # If we step onto a resource, strongly prefer it.
        if (nx, ny) in resources:
            val += 10**6

        # Deterministic tie-break: prefer smaller dx,dy in lexicographic order implicitly by comparing (val, -dx,-dy)
        key = (val, -dx, -dy)
        if key > (best_val, -best_move[0], -best_move[1]):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]