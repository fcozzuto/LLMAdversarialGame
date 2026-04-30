def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in dirs:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    # Pick a target resource where we're relatively advantaged; alternate preference by turn parity.
    turn = int(observation.get("turn_index", 0) or 0)
    sign = 1 if (turn % 2 == 0) else -1
    best_target = None
    best_key = None
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Lower is better: we prefer resources where (self - opp) is small/negative.
            key = (ds - do, ds, sign * (ds + do))
            if best_key is None or key < best_key:
                best_key = key
                best_target = (rx, ry)
    else:
        best_target = (ox, oy)

    tx, ty = best_target
    best_move = (0, 0)
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)

        # Safety: prefer moves that keep farther from opponent when parity wants disruption.
        nd = cheb(nx, ny, ox, oy)
        nopp_adv = cheb(ox, oy, tx, ty)

        # If we are far behind on this target, prioritize moving away from opponent.
        back = cheb(sx, sy, tx, ty) - nopp_adv
        away_weight = 2 if (back > 0 and (turn % 2 == 1)) else 0

        score = (ns, away_weight * (-nd), cheb(nx, ny, sx, sy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]