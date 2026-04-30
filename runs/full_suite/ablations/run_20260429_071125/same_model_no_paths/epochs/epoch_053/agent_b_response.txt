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

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not free(sx, sy):
        for dx, dy in moves[1:]:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = (-(10**9), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Choose the resource opponent is currently closest to; try to beat that race.
    target = None
    best_op = 10**9
    for tx, ty in resources:
        d = cheb(ox, oy, tx, ty)
        if d < best_op:
            best_op = d
            target = (tx, ty)

    tx, ty = target
    my_now = cheb(sx, sy, tx, ty)
    opp_now = best_op

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        opp_d = opp_now  # optimistic: opponent position won't change this turn
        # Primary: capture if reachable
        capture_bonus = 1000 if (nx, ny) == (tx, ty) else 0
        # Secondary: increase distance advantage against the target
        score = capture_bonus + (opp_d - my_d)
        # Tertiary: avoid getting worse if we're already close
        score -= (my_d - my_now) * 0.5
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]