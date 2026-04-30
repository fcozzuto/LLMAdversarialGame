def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Prefer resources we can reach no later than opponent, then closest, deterministic tie-break.
    def res_value(nx, ny, rx, ry):
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive => we are closer
        return lead * 10 - ds  # lexicographic-ish

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Evaluate best resource from this next cell; deterministic tie-break via ordering.
        local_best = -10**18
        local_r = None
        for rx, ry in resources:
            v = res_value(nx, ny, rx, ry)
            if v > local_best:
                local_best = v
                local_r = (rx, ry)
        # Secondary tie-break: prefer shorter ds and then lower (rx,ry) lexicographically.
        if local_r is not None:
            rx, ry = local_r
            ds = cheb(nx, ny, rx, ry)
            score = (local_best, -ds, -rx, -ry)
        else:
            score = (local_best, 0, 0, 0)
        if score > (best_score, 0, 0, 0):
            best_score = score[0]
            best_move = [dx, dy]

    return best_move