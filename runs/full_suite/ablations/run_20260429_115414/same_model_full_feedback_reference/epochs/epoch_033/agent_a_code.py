def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
        if not valid(tx, ty):
            tx, ty = sx, sy
    else:
        me = (sx, sy)
        foe = (ox, oy)
        tx, ty = resources[0]
        best = None
        for r in resources:
            ds = dist(me, r)
            do = dist(foe, r)
            adv = do - ds
            tie = (ds, r[0], r[1])
            key = (adv, -ds, -do, -((r[0] - sx) ** 2 + (r[1] - sy) ** 2), -tie[0], tie[1], tie[2])
            if best is None or key > best:
                best = key
                tx, ty = r

    cur = (sx, sy)
    target = (tx, ty)
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist((nx, ny), target)
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]