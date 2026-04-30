def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd, best = d, (dx, dy)
        return [best[0], best[1]]

    # Evaluate moves by advantage (opp_dist - my_dist) to the most relevant resources.
    # Also bias toward breaking ties on closer resources.
    res_sorted = sorted(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
    k = 3 if len(res_sorted) >= 3 else len(res_sorted)
    chosen = res_sorted[:k]

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        for i, (tx, ty) in enumerate(chosen):
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Strongly prefer resources where we can beat/keep up with opponent.
            gap = opd - myd
            score += (10 - i) * gap
            # Penalize getting farther from already-closest target.
            score -= i * (myd - cheb(sx, sy, tx, ty))
        # Deterministic tie-break: prefer staying closer to the nearest chosen resource.
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            cur_best_dist = cheb(sx + best_move[0], sy + best_move[1], chosen[0][0], chosen[0][1])
            cand_dist = cheb(nx, ny, chosen[0][0], chosen[0][1])
            if cand_dist < cur_best_dist:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]