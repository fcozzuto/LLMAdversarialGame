def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Precompute local "resource density" around each resource for stable targeting.
    dens = {}
    for tx, ty in resources:
        c = 0
        for rx, ry in resources:
            if md(tx, ty, rx, ry) <= 2:
                c += 1
        dens[(tx, ty)] = c

    best_val = None
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Choose the most favorable target from this candidate position.
        my_best = None
        for tx, ty in resources:
            myd = md(nx, ny, tx, ty)
            opd = md(ox, oy, tx, ty)
            # Primary: maximize distance advantage; Secondary: prefer closer targets; Tertiary: density.
            key = (-(opd - myd), myd, -dens[(tx, ty)], tx, ty)
            if my_best is None or key < my_best[0]:
                my_best = (key, (tx, ty), myd, opd)

        if my_best is None:
            continue

        _, (tx, ty), myd, opd = my_best
        # Value favors winning the contest for a dense cluster and keeps some separation from opponent.
        val = (opd - myd) + 0.15 * dens[(tx, ty)] + 0.02 * md(nx, ny, ox, oy) - 0.001 * myd

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]