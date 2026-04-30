def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Drift toward opponent corner to avoid being stuck, while not hitting obstacles
        tx, ty = (w - 1, 0) if (ox + oy) > (sx + sy) else (0, h - 1)
        best = (None, -10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            score = -cheb(nx, ny, tx, ty)
            if score > best[1]:
                best = ((dx, dy), score)
        return [best[0][0], best[0][1]] if best[0] is not None else [0, 0]

    # Choose move that maximizes advantage on the best contestable resource.
    best_move = (0, 0)
    best_score = -10**18

    # Deterministic tie-breakers: score, then distance, then lexicographic move (by dirs order)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate against best target from this next position
        local_best = -10**18
        local_dist = 10**9
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)

            # Prefer resources where we are closer (or will be closer), and closer pick-up.
            # Large weight on contest advantage; small penalty on our distance.
            adv = d_opp - d_self  # higher is better
            score = 1000 * adv - 2 * d_self

            # Mild preference for not giving immediate access to opponent (smaller d_opp after our move is also fine)
            # Deterministic and simple: add tiny term to prefer resources more central to us.
            score += -0.01 * (cheb(ox, oy, rx, ry))

            if score > local_best or (score == local_best and d_self < local_dist):
                local_best = score
                local_dist = d_self

        if local_best > best_score:
            best_score = local_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]