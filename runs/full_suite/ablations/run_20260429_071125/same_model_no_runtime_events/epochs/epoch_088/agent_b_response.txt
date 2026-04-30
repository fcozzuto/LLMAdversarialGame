def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # If no resources, head toward opponent's side while avoiding obstacles
    if not resources:
        tx, ty = (w - 1, h - 1) if ox >= (w - 1) // 2 else (0, h - 1)
        best = None
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            val = -cheb(nx, ny, tx, ty)
            if best_val is None or val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Choose move maximizing (opponent distance to best contestable resource) - (our distance after move)
    best_move = (0, 0)
    best_margin = None
    best_our_dist = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        our_d = None
        # select resource that gives maximal contest margin for this candidate
        cand_best = None
        cand_margin = None
        for rx, ry in resources:
            d_opp = cheb(ox, oy, rx, ry)
            d_our = cheb(nx, ny, rx, ry)
            margin = d_opp - d_our
            if cand_margin is None or margin > cand_margin:
                cand_margin = margin
                cand_best = d_our
        our_d = cand_best
        if best_margin is None or cand_margin > best_margin or (cand_margin == best_margin and our_d < best_our_dist):
            best_margin = cand_margin
            best_our_dist = our_d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]