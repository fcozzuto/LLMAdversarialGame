def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Fallback: move to maximize distance from opponent (defensive)
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = man(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose target resource: prefer those we can reach earlier than opponent, break ties by closeness to us
    best_r = resources[0]
    best_key = (-10**18, -10**18)
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Relative advantage: positive is we are closer
        rel = do - ds
        # Slight bias to nearer resources and to overall advancement toward opponent side
        adv = (ds * 0.0)  # keep deterministic placeholder minimal
        bias = -ds - 0.02 * (rx + ry)  # prefer smaller ds, deterministic bias
        key = (rel, bias)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # If opponent is closer to target, try to intercept by moving to a cell that reduces their distance to target most
    # while not increasing ours too much.
    my_d = man(sx, sy, tx, ty)
    op_d = man(ox, oy, tx, ty)
    contest = op_d <= my_d

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = man(nx, ny, tx, ty)
        no = man(ox, oy, tx, ty)  # unchanged by our move
        # Primary: reduce distance to target
        score = (my_d - ns) * 10.0 - ns
        # Secondary: if contesting, also discourage moves that give opponent an easier time to reach (proxy: maximize distance from opponent after move)
        score += 0.35 * man(nx, ny, ox, oy)
        if contest:
            # Favor moves that keep us nearer while making target less accessible to opponent via spatial proximity (proxy by cutting their distance to us)
            score -= 0.25 * man(nx, ny, ox, oy)  # tradeoff: if we're not closer, keep pressure rather than purely fleeing
            score += 0.1 * (op_d - ns)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]