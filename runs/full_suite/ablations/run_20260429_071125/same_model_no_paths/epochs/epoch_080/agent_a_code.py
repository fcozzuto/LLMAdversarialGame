def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    # Strong change: evaluate each immediate move by best attainable resource advantage,
    # with heavy penalty when opponent is closer, and a small term to avoid ceding space.
    best_move = (0, 0, None)
    best_score = None
    for dx, dy, nx, ny in moves:
        move_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are strictly closer; if tied or behind, only take if very close.
            adv = opd - myd
            # Also discourage walking away from all resources.
            closeness = 20 - myd
            tie = 1 if adv == 0 else 0
            behind_pen = -5000 if adv < 0 else 0
            score = adv * 2000 + closeness * 50 + tie * 10 + behind_pen
            # Deterministic micro-bias toward lower coordinates for tie-breaking.
            score -= rx * 2 + ry
            if score > move_score:
                move_score = score
        # Small preference to not allow opponent to get strictly closer to us.
        my2 = cheb(nx, ny, ox, oy)
        score2 = move_score - my2
        if best_score is None or score2 > best_score:
            best_score = score2
            best_move = (dx, dy, score2)
    return [int(best_move[0]), int(best_move[1])]