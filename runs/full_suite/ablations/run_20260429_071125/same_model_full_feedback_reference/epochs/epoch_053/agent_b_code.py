def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if resources:
        best_d = None
        best = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            if best_d is None or ds < best_d or (ds == best_d and (x, y) < best):
                best_d = ds
                best = (x, y)
        target = best

    tx, ty = target if target is not None else (w // 2, h // 2)
    if target is None and resources:
        tx, ty = resources[0]

    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        res_bonus = 0
        if resources:
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    res_bonus = 5
                    break
        score = -d_self + 0.15 * d_opp + res_bonus
        moves.append((score, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [moves[0][1], moves[0][2]]