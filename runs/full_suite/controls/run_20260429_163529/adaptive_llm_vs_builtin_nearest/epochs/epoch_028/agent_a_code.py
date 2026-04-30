def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] if len(op) > 0 else w - 1), int(op[1] if len(op) > 1 else h - 1)

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    res = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])
    self_best = min(res, key=lambda r: man((sx, sy), r))
    opp_best = min(res, key=lambda r: man((ox, oy), r))

    ds_self = man((sx, sy), self_best)
    ds_opp_to_opp_best = man((ox, oy), opp_best)
    ds_self_to_opp_best = man((sx, sy), opp_best)

    # If we can reach opponent's closest resource faster or about as fast, contest it.
    if ds_self_to_opp_best + 0.1 < ds_opp_to_opp_best:
        target = opp_best
        target_mode = 1.0
    else:
        target = self_best
        target_mode = 0.0

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                m += 1
        return m

    best_move = legal[0]
    best_val = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self = man((nx, ny), target)
        d_opp = man((ox, oy), opp_best)
        # Aim to both get closer to target and avoid letting opponent improve their access.
        opp_score = d_opp - man((ox, oy), self_best)
        # Use local mobility to avoid getting stuck behind obstacles.
        val = d_self + (1.2 - 0.5 * target_mode) * (-opp_score) - 0.05 * mobility(nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]