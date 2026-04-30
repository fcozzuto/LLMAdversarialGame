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

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def near_obs_pen(nx, ny):
        pen = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                tx, ty = nx + dx, ny + dy
                if (tx, ty) in obstacles:
                    pen += 2
        return pen

    best = None
    bestv = -10**18
    # Strategy: pick the move that maximizes "capture advantage" over opponent for the best resource,
    # with strong deterrence for entering obstacle-adjacent cells.
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue
        my_now = cheb(nx, ny, ox, oy)
        v = -near_obs_pen(nx, ny)
        # Bonus for moving such that we reduce our distance to a winning resource
        # while increasing opponent distance.
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            if d_me == 0:
                # immediate collection preferred strongly
                v += 10_000 - 3 * my_now
                continue
            # Advantage: positive means we are closer than opponent would be to the same resource
            adv = d_op - d_me
            # Encourage selecting resources where we can plausibly be first soon
            urgency = 8 - d_me
            v += (adv * 25) + (urgency * 3)
        # Small tie-break: prefer reducing our distance to opponent (denial pressure)
        v += -my_now
        if v > bestv:
            bestv = v
            best = (mdx, mdy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]