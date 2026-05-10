def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    cand_moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def detour_dist(ax, ay, tx, ty):
        dx = tx - ax
        dy = ty - ay
        d = abs(dx) + abs(dy)
        # obstacle-aware penalty: if an obstacle lies on an axis-aligned monotone route, add 1
        for (bx, by) in obstacles:
            if bx == ax and min(ay, ty) <= by <= max(ay, ty):  # vertical segment
                if by != ay and by != ty:
                    d += 1
            if by == ay and min(ax, tx) <= bx <= max(ax, tx):  # horizontal segment
                if bx != ax and bx != tx:
                    d += 1
        return d

    def blocked(nx, ny):
        return not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles

    def score_resource(tx, ty):
        myd = detour_dist(sx, sy, tx, ty)
        opd = detour_dist(ox, oy, tx, ty)
        # favor clear advantage; slight preference for closer targets
        return (opd - myd) * 100 - myd

    target = None
    best = -10**18
    for (tx, ty) in resources:
        s = score_resource(tx, ty)
        if s > best:
            best = s
            target = (tx, ty)

    tx, ty = target
    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in cand_moves:
        nx, ny = sx + dxm, sy + dym
        if blocked(nx, ny):
            continue
        # progress toward target plus keep out of trouble
        myd_next = detour_dist(nx, ny, tx, ty)
        opd = detour_dist(ox, oy, tx, ty)
        val = (opd - myd_next) * 100 - myd_next
        # tie-break: move diagonally when equally good; and avoid staying if progress possible
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)
        elif val == best_val:
            if (dxm != 0 and dym != 0) and not (best_move[0] != 0 and best_move[1] != 0):
                best_move = (dxm, dym)
            elif (dxm == 0 and dym == 0) and not (best_move[0] == 0 and best_move[1] == 0):
                best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]