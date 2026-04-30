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

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inside(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def choose_target():
        if not resources:
            return None
        best = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            margin = do - ds
            # also prefer closer resources in tie
            score = (margin * 1000) - (ds * 5) - (x + y)
            if best is None or score > best[0]:
                best = (score, x, y)
        return (best[1], best[2]) if best else resources[0]

    tx = ty = None
    target = choose_target()
    if target is not None:
        tx, ty = target

    # If opponent is very close to us, stabilize by stepping away slightly (deterministic).
    opp_dist = cheb(sx, sy, ox, oy)
    away_bias = opp_dist <= 2

    best_move = (0, 0, -10**9)  # dx,dy,score
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Primary: reduce distance to target; Secondary: avoid giving opponent an easy race.
        if target is not None:
            myd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # If opponent is ahead, slightly deprioritize continuing in same direction by penalizing closeness for us.
            race_pen = (od - myd) < 0
            score = -myd * 10 + (od - myd) * 2
            if race_pen:
                score -= 8
        else:
            score = 0

        if away_bias:
            my_to_op = cheb(nx, ny, ox, oy)
            score += my_to_op * 3

        # Mild obstacle-aware preference: prefer moves that don't increase distance to center-ish (helps break ties).
        score -= abs(nx - (w - 1) / 2) * 0.01 + abs(ny - (h - 1) / 2) * 0.01

        if score > best_move[2]:
            best_move = (dx, dy, score)

    return [best_move[0], best_move[1]]