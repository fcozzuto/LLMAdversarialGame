def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs_list = observation.get("obstacles") or []
    obs = set()
    for p in obs_list:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res_list = observation.get("resources") or []
    resources = []
    for r in res_list:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if resources:
        best_t = resources[0]
        best_s = -10**18
        for t in resources:
            sd = man((sx, sy), t)
            od = man((ox, oy), t)
            score = (od - sd) * 10 - sd
            if score > best_s:
                best_s = score
                best_t = t
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_t = (cx, cy)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        val = -man((nx, ny), (tx, ty))
        if resources:
            # Prefer moves that also deny: closer to chosen target than opponent
            val += 2 * (man((ox, oy), (tx, ty)) - man((nx, ny), (tx, ty)))
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]