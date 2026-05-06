def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
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

    def kingdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        if 0 <= sx + dx < w and 0 <= sy + dy < h and (sx + dx, sy + dy) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best = None
    best_adv = -10**9
    best_my_close = 10**9
    tie = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue

        adv = -10**9
        my_close = 10**9
        pick = None
        for rx, ry in resources:
            myd = kingdist(nx, ny, rx, ry)
            opd = kingdist(ox, oy, rx, ry)
            if (opd - myd) > adv or ((opd - myd) == adv and myd < my_close):
                adv = opd - myd
                my_close = myd
                pick = (rx, ry)

        # Prefer blocking: maximize advantage, then minimize our distance, then move that also reduces opp-nearest resource distance
        if pick is None:
            continue
        rx, ry = pick
        oppd_pick = kingdist(ox, oy, rx, ry)
        myd_pick = kingdist(nx, ny, rx, ry)
        key = (-adv, myd_pick, oppd_pick, abs(nx - sx) + abs(ny - sy), dx, dy)
        if best is None or key < best:
            best = key
            tie = (dx, dy)
            best_adv = adv
            best_my_close = my_close

    if tie is None:
        return [0, 0]
    return [int(tie[0]), int(tie[1])]