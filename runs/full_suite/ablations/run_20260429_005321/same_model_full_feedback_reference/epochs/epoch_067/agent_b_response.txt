def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx = 0 if sx + ox <= (w - 1) else (w - 1)
        ty = 0 if sy + oy <= (h - 1) else (h - 1)
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                key = (d2(nx, ny, tx, ty), d2(ox, oy, tx, ty))
                if best is None or key < best[0]:
                    best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    # One-step lookahead: pick move that maximizes (opponent needs longer to reach our chosen target than we do),
    # while also preferring smaller absolute distance.
    best_key = None
    best_move = (0, 0)
    for dxm, dym in moves:
        nsx, nsy = sx + dxm, sy + dym
        if not ok(nsx, nsy):
            continue
        candidate = None
        # Choose the resource for which we gain the most "reach advantage" after this move.
        for rx, ry in resources:
            my = d2(nsx, nsy, rx, ry)
            oy_d = d2(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent; if none, pick closest by us.
            reach_adv = oy_d - my
            key = (-reach_adv, my, rx, ry)
            # We want minimal key: maximize reach_adv, then minimize my.
            if candidate is None or key < candidate[0]:
                candidate = (key, (rx, ry), reach_adv, my, oy_d)
        if candidate is None:
            continue
        _, (rx, ry), reach_adv, my, oy_d = candidate
        # Final scoring: primary is reach_adv (bigger better), then prioritize safety (keep away from opponent's closest resource).
        my_close = my
        opp_close = oy_d
        # Secondary: slightly avoid moving closer to opponent unless we have reach advantage.
        opp_dist_after = d2(nsx, nsy, ox, oy)
        score_key = (-(reach_adv if reach_adv > 0 else reach_adv - 0.5), my_close, opp_dist_after, rx, ry)
        if best_key is None or score_key < best_key:
            best_key = score_key
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]