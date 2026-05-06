def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obst:
                pen += 1
        return pen

    if not resources:
        return [0, 0]

    # Pick a target where we have deterministic positional advantage now
    best_r = None
    best_key = None
    for rx, ry in resources:
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        adv = opp_d - self_d  # larger means we are closer than opponent
        # prefer strong advantage; otherwise nearer and farther-from-opponent
        key = (-adv, self_d, -opp_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = [0, 0]
    best_eval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        self_d2 = man(nx, ny, tx, ty)
        opp_d = man(ox, oy, tx, ty)
        adv2 = opp_d - self_d2
        pen = adj_obst_pen(nx, ny)
        # maximize adv2, then minimize self distance, then reduce obstacle proximity
        # deterministic tie-break by move order
        eval_key = (-adv2, self_d2, pen, dx, dy)
        if best_eval is None or eval_key < best_eval:
            best_eval = eval_key
            best_move = [dx, dy]

    return best_move