def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def valid_cell(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if valid_cell(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    low_left = observation.get("remaining_resource_count", len(res))
    few = 1 if low_left <= 3 else 0

    best = None
    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # win-likelihood proxy: prefer where we are closer than opponent (higher od-sd)
        adv = (od - sd)
        # when few left, prioritize securing quickly
        if few:
            adv = adv * 2 - sd
        # tiny tie-break: prefer targets not exactly on opponent axis (reduces opponent sweep)
        if rx == ox:
            adv -= 0.15
        if ry == oy:
            adv -= 0.15
        cand = (adv, -sd, -rx, -ry, rx, ry)
        if best is None or cand > best:
            best = cand
            target = (rx, ry)

    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    cur_best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid_cell(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        # keep target pressure while not walking into obstacles (handled above)
        val = (od2 - sd2, -sd2, -abs(nx - ox) - abs(ny - oy), -abs(nx - tx) - abs(ny - ty))
        if cur_best is None or val > cur_best:
            cur_best = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]