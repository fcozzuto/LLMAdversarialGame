def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = W - 1 - sx, H - 1 - sy
        best = (-10**9, 10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (-d, d, -abs(nx - ox) - abs(ny - oy), dx, dy) > best:
                best = (-d, d, -abs(nx - ox) - abs(ny - oy), dx, dy)
        return [best[3], best[4]]

    best = (-10**9, 10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        op_d = 10**9
        me_d = 10**9
        best_urgency = -10**9
        for rx, ry in resources:
            dme = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dme < me_d: me_d = dme
            if dop < op_d: op_d = dop
            urgency = dop - dme  # higher means we beat opponent to it
            if urgency > best_urgency: best_urgency = urgency
        # Primary: maximize urgency; Secondary: minimize our distance; Tertiary: maximize opponent distance
        key = (best_urgency, -me_d, op_d, -dx, -dy)
        if key > (best[0], -best[1], best[2], -best[3], -best[4]):
            best = (best_urgency, me_d, op_d, dx, dy)

    return [best[3], best[4]]