def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Head toward center, but keep a deterministic bias away from staying too long.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = cheb(nx, ny, cx, cy) * 10 - cheb(nx, ny, ox, oy)
            if bestv is None or v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    # Choose move that maximizes relative advantage to the best target resource.
    # Score = opp_distance - my_distance, with small tie-break toward reducing my distance to that target.
    best_move = (0, 0)
    best_score = None
    best_tie = None
    rx_bias = sorted(resources)  # deterministic tie handling
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        local_best_score = None
        local_best_tie = None
        for tx, ty in rx_bias:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            s = opd - myd
            t = myd
            if local_best_score is None or s > local_best_score or (s == local_best_score and t < local_best_tie):
                local_best_score, local_best_tie = s, t
        # Global compare: prefer higher advantage; if equal, prefer smaller my distance to that chosen target.
        if best_score is None or local_best_score > best_score or (local_best_score == best_score and local_best_tie < best_tie):
            best_score, best_tie = local_best_score, local_best_tie
            best_move = (dx, dy)

    # If constrained, ensure move is valid (engine would otherwise keep us anyway, but be safe).
    if not ok(sx + best_move[0], sy + best_move[1]):
        return [0, 0]
    return [best_move[0], best_move[1]]