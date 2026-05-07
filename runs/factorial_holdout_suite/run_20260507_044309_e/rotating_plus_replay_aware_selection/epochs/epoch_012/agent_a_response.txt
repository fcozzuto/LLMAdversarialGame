def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def opp_step(tx, ty, px, py):
        # opponent moves greedily toward (tx,ty) with deterministic tie-break:
        # prefer moves with smallest cheb, then prefer larger dx, then larger dy.
        best = None
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not valid(nx, ny):
                nx, ny = px, py
            d = cheb(nx, ny, tx, ty)
            cand = (d, -dx, -dy, nx, ny)
            if best is None or cand < best:
                best = cand
        return best[3], best[4]

    best_score = None
    best_move = (0, 0)
    for tx, ty in resources:
        if (tx, ty) in obstacles:
            continue
        # consider our move that best advances to (tx,ty)
        for dx, dy in moves:
            nsx, nsy = sx + dx, sy + dy
            if not valid(nsx, nsy):
                nsx, nsy = sx, sy
            ds = cheb(nsx, nsy, tx, ty)
            # predict opponent one step greedily toward same resource
            nox, noy = opp_step(tx, ty, ox, oy)
            do = cheb(nox, noy, tx, ty)
            # higher is better: we want to be closer than opponent after their step
            center_bias = -0.02 * cheb(nsx, nsy, w // 2, h // 2)
            block_bonus = 0.0
            if not valid(nox, noy) or (nox, noy) in obstacles:
                block_bonus = 1.5
            score = (do - ds) + center_bias + block_bonus - 0.03 * ds
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]