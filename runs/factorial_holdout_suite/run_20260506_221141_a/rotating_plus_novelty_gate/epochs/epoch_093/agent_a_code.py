def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)
    moves = [(dx, dy) for dx in dxs for dy in dys]
    if (0, 0) not in moves:
        moves.append((0, 0))

    def md(ax, ay, bx, by):
        ddx = ax - bx
        if ddx < 0: ddx = -ddx
        ddy = ay - by
        if ddy < 0: ddy = -ddy
        return ddx if ddx > ddy else ddy

    cur = (sx, sy)
    if not resources:
        best = (0, 0)
        best_val = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
                continue
            # Move toward opponent to pressure when no resources known.
            val = -md(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        my_best = 10**9
        op_best = 10**9
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if opd < op_best:
                op_best = opd

        # Prefer moves that get us closer than opponent to some resource,
        # otherwise reduce opponent's advantage.
        adv = op_best - my_best  # positive is good for us
        val = adv * 1000 - my_best
        if adv <= 0:
            val -= (my_best + op_best)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]