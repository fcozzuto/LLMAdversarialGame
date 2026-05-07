def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose a target that we can reach first (or at least denies opponent most).
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        adv = od - sd  # higher is better for us
        key = (adv, -sd, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    (adv, _, tx, ty) = best[0]
    target = best[1]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # For our move, maximize: (opponent distance - our distance) to target, with stability tie-breaks.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = md(nx, ny, target[0], target[1])
        opd = md(ox, oy, target[0], target[1])
        val = (opd - myd, -myd, -md(nx, ny, tx, ty), -(abs(nx - ox) + abs(ny - oy)))
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]