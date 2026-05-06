def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for yy in range(h):
            for xx in range(w):
                if valid(xx, yy):
                    sx, sy = xx, yy
                    break
            if valid(sx, sy):
                break
    if not resources:
        # Defensive: step to maximize (our distance - opponent distance)
        best = [0, 0, -10**9]
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not valid(nx, ny):
                    continue
                s = man(nx, ny, sx, sy)  # stable move
                gain = man(nx, ny, ox, oy) - man(sx, sy, ox, oy)  # increase opponent distance
                val = 1000 * gain + 2 * s
                if val > best[2]:
                    best = [dx, dy, val]
        return [int(best[0]), int(best[1])]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # Offensive-besides-interceptor: choose move that improves our next target and also delays opponent.
    best_dx, best_dy, best_val = 0, 0, -10**18
    for dx, dy, nx, ny in moves:
        our_d = man(nx, ny, ox, oy)  # closer means risk; farther means safer
        local_best = 10**9
        delay_best = -10**9
        for rx, ry in resources:
            d_self = man(nx, ny, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # We prefer resources we can reach sooner; also prefer those where our move increases gap vs opponent.
            gap_after = (d_opp - d_self)
            # Slightly bias towards resources that are closer to us than to opponent currently.
            bias = 1 if (man(sx, sy, rx, ry) <= d_opp) else 0
            score = -d_self + 0.9 * gap_after + 0.15 * bias
            if score > local_best:
                local_best = score
            if gap_after > delay_best:
                delay_best = gap_after
        # Combine: maximize reaching + delay, but avoid stepping too close to opponent if scores tie.
        val = 10 * local_best + 0.7 * delay_best + 0.01 * our_d
        if val > best_val or (val == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = val
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]