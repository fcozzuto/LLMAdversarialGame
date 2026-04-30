def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []) if len(p) >= 2)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    taken_here = any((sx == r[0] and sy == r[1]) for r in resources if len(r) >= 2)
    if taken_here:
        return [0, 0]

    cx, cy = (w - 1) // 2, (h - 1) // 2

    # Pre-rank resources by "net advantage" we should pursue this turn.
    best_tar = None
    for r in resources:
        if len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Encourage being closer than opponent; slight center bias; discourage far targets.
        net = (opd - myd) * 100 - myd + (-cheb(rx, ry, cx, cy))
        if best_tar is None or net > best_tar[0]:
            best_tar = (net, rx, ry)
    if best_tar is None:
        return [0, 0]
    tx, ty = best_tar[1], best_tar[2]

    # Evaluate a move by progress to target and improvement in our advantage vs opponent.
    cur_myd = cheb(sx, sy, tx, ty)
    cur_opd = cheb(ox, oy, tx, ty)
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # Estimate opponent pressure by assuming opponent stays similar (short horizon).
        # Prefer moves that reduce our distance more than what the opponent likely gains.
        # Also avoid letting opponent get strictly better advantage than us.
        my_adv = (cur_opd - myd) - (cur_opd - cur_myd)
        # Compromise: primary is reaching/closing target; secondary is center.
        center = -cheb(nx, ny, cx, cy)
        # Tertiary: don't increase our distance to the best target.
        progress = -(myd)
        # Combine with bonus for taking lead when tied/close.
        lead_bonus = 0
        if myd <= cur_opd:
            lead_bonus = 20 if myd < cur_opd else 5
        score = (my_adv * 30) + (progress * 10) + center + lead_bonus
        if best is None or score > best[0]:
            best = (score, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]