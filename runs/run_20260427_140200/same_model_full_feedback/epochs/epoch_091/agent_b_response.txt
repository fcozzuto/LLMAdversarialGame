def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        # fallback: move toward center away from opponent a bit
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = (cheb(nx, ny, cx, cy) * 2) - cheb(nx, ny, ox, oy)
            if best is None or v < best[0] or (v == best[0] and (dx, dy) < best[1]):
                best = (v, (dx, dy))
        return best[1] if best else [0, 0]

    # Candidate move scoring: maximize advantage for at least one resource,
    # and if opponent is closer to it, prioritize reducing that gap.
    best_score = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # avoid getting too close to opponent unless it also improves resource advantage
        opp_adj_pen = 0
        d_to_opp = cheb(nx, ny, ox, oy)
        if d_to_opp <= 1:
            opp_adj_pen = 0.35

        # compute best advantage over resources
        local_best = None
        for rx, ry in resources:
            d_s = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            # Advantage: positive if we are closer than opponent to that resource
            # Also prefer moving closer even when we aren't yet ahead.
            adv = (d_o - d_s)
            # Secondary: slight preference for nearer target from our next position
            tie = -0.03 * d_s
            val = adv + tie
            if local_best is None or val > local_best:
                local_best = val

        score = local_best - opp_adj_pen

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]