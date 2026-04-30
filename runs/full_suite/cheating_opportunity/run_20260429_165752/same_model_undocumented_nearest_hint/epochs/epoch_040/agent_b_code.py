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

    res = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                res.append((x, y))
    res = list(dict.fromkeys(res))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    if res:
        for x, y in res:
            d_s = dist(sx, sy, x, y)
            d_o = dist(ox, oy, x, y)
            score = 0
            if d_s == 0:
                score = 10**9
            else:
                score = (d_o - d_s) * 100 - d_s
            candidates.append((-(score), x, y))
        candidates.sort()
    else:
        candidates = [(0, ox, oy)]

    best = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        if candidates and res:
            _, tx, ty = candidates[0]
            d_s = dist(nx, ny, tx, ty)
            d_o = dist(ox, oy, tx, ty)
            val = (d_o - d_s) * 100 - d_s
            if (nx, ny) in res:
                val += 10**6
        else:
            d_to_opp = dist(nx, ny, ox, oy)
            val = -d_to_opp
        if best is None or val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]