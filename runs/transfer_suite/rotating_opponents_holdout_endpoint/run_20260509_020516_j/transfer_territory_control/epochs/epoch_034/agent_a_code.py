def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    ex, ey = observation.get("opponent_position", (W - 1, H - 1))
    ex, ey = int(ex), int(ey)

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    opp_t = set()
    for p in observation.get("opponent_territory") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                opp_t.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if res:
        tx, ty = min(res, key=lambda t: (man(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        best = None
        for p in observation.get("unclaimed_cells") or []:
            if p and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                    score = (man(ex, ey, x, y) - man(sx, sy, x, y), x, y)
                    if best is None or score > best[0]:
                        best = (score, x, y)
        if best is None:
            tx, ty = W // 2, H // 2
        else:
            tx, ty = best[1], best[2]

    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1), (0, 0)]
    cur_best = None
    cur_dxdy = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < W and 0 <= ny < H):
            continue
        if (nx, ny) in obs:
            continue
        penalty = 200000 if (nx, ny) in opp_t else 0
        dcur = man(nx, ny, tx, ty)
        key = (penalty + dcur, penalty, -man(nx, ny, ex, ey), dx, dy)
        if cur_best is None or key < cur_best:
            cur_best = key
            cur_dxdy = (dx, dy)
    dx, dy = cur_dxdy
    return [int(dx), int(dy)]