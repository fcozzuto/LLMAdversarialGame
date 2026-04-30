def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def dir_step(x, y, tx, ty):
        dx = tx - x
        if dx > 0: sx1 = 1
        elif dx < 0: sx1 = -1
        else: sx1 = 0
        dy = ty - y
        if dy > 0: sy1 = 1
        elif dy < 0: sy1 = -1
        else: sy1 = 0
        return sx1, sy1

    # Choose target: prefer resources we can reach no worse than opponent,
    # otherwise the resource that least favors opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Primary: larger advantage for us; Secondary: closer for us; Tertiary: deterministic by coords
        adv = opd - myd
        key = (adv, -myd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    # Greedy one-step toward target with obstacle avoidance; tie-break deterministically.
    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    preferred_dx, preferred_dy = dir_step(sx, sy, tx, ty)
    best_move = (0, 0)
    best_val = None
    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # If we can't improve reach, we still prefer the move that reduces opponent's advantage on the same target.
        opd2 = cheb(ox, oy, tx, ty)
        val = (-myd2, (opd2 - myd2), -(abs(dx - preferred_dx) + abs(dy - preferred_dy)), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]