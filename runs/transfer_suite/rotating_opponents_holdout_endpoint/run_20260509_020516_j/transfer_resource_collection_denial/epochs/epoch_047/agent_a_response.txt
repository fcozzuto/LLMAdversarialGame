def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    best_score = -10**18

    # Deterministic preference ordering among equal scores
    order = {(0, 0): 0, (1, 0): 1, (-1, 0): 2, (0, 1): 3, (0, -1): 4,
             (1, 1): 5, (1, -1): 6, (-1, 1): 7, (-1, -1): 8}

    for dx, dy, nx, ny in moves:
        self_pos = (nx, ny)
        # Pick target resource that maximizes advantage from this move
        local_best = -10**18
        for tx, ty in resources:
            sd = cheb(self_pos[0], self_pos[1], tx, ty)
            od = cheb(ox, oy, tx, ty)
            # Prefer being closer than opponent; strongly penalize where opponent is closer
            adv = od - sd
            score = adv * 1000 - sd
            if score > local_best:
                local_best = score
        if local_best > best_score:
            best_score = local_best
            best = (dx, dy)
        elif local_best == best_score:
            if order[(dx, dy)] < order[best]:
                best = (dx, dy)

    return [int(best[0]), int(best[1])]