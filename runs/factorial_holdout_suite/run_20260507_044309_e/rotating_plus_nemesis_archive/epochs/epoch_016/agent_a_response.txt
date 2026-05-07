def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except:
        sx, sy, ox, oy = 0, 0, 0, 0

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    if not res:
        # drift toward center while avoiding obstacles
        center = (w // 2, h // 2)
        best = (0, 0, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = dist((nx, ny), center)
            key = (d, abs(nx - center[0]) + abs(ny - center[1]), 0)
            if d < best[2]:
                best = (dx, dy, d)
        return [best[0], best[1]]

    # Target selection: prioritize resources where we can get earlier than opponent, then closer to us.
    best_t = res[0]
    best_key = None
    for t in res:
        sd = dist((sx, sy), t)
        od = dist((ox, oy), t)
        # maximize: margin (od - sd) then minimize sd
        key = (od - sd, -sd)
        if best_key is None or key > best_key:
            best_key = key
            best_t = t

    tx, ty = best_t
    cur_sd = dist((sx, sy), (tx, ty))

    # Choose legal move that most reduces distance to target; tie-break by minimizing opponent distance after move.
    best_move = (0, 0)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = abs(nx - tx) + abs(ny - ty)
        od = abs(nx - ox) + abs(ny - oy)
        # prefer progress; if no progress, still prefer lower opponent distance
        key = (-(nd - cur_sd), -nd, -od, dx, dy)
        if best is None or key > best:
            best = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]