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
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # If no visible resources, drift toward center to reduce stalemates
    if not resources:
        tx, ty = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [int(best[1]), int(best[2])]

    # Choose a resource to maximize "win" probability: we should be closer than opponent
    best_move = None
    best_score = -10**18

    # Precompute a target ordering of resources by a deterministic key
    res = sorted(resources, key=lambda r: (md(sx, sy, r[0], r[1]), r[0], r[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Avoid moving into tight proximity with opponent unless it improves resource claim
        opp_d = md(nx, ny, ox, oy)
        danger = -2.0 if opp_d <= 1 else (-0.8 if opp_d <= 2 else 0.0)

        # Evaluate best resource for this candidate move
        move_best = -10**18
        for rx, ry in res[:min(6, len(res))]:
            myd = md(nx, ny, rx, ry)
            opd = md(ox, oy, rx, ry)
            # Positive if we get to it earlier; strong bonus for immediate pickup
            claim = (opd - myd)
            immediate = 8.0 if (nx == rx and ny == ry) else 0.0
            # Prefer resources that are not currently "safer" for opponent
            # (if we are not significantly closer, it will score lower)
            score = 2.2 * claim - 0.25 * myd + immediate
            # Slight preference for resources away from opponent to reduce contention
            score += 0.12 * (opd - myd)
            if score > move_best:
                move_best = score

        total = move_best + danger
        cand = (total, -abs(dx) - abs(dy), dx, dy)
        if best_move is None or cand > best_move:
            best_move = cand
            best_score = total

    # Deterministic tie-break among moves with equal score: smallest dx, then dy (lex)
    if best_move is None:
        return [0, 0]
    return [int(best_move[2]), int(best_move[3])]