def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # Targeting: pick resource that maximizes our advantage (opp_dist - my_dist),
    # with a secondary bias toward central area to reduce tail-chasing.
    cx, cy = w // 2, h // 2
    best_target = None
    best_tscore = None
    for r in resources:
        if not r or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        myd = md(sx, sy, rx, ry)
        oppd = md(ox, oy, rx, ry)
        tscore = (oppd - myd) * 10 - md(rx, ry, cx, cy)
        if best_tscore is None or tscore > best_tscore:
            best_tscore = tscore
            best_target = (rx, ry)

    if best_target is None:
        # Fallback: head toward center if no resources.
        tx, ty = cx, cy
    else:
        tx, ty = best_target

    # Choose move that improves our distance to target and also keeps us from
    # becoming closer than the opponent by too much for contested resources.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = int(sx + dx), int(sy + dy)
        if not valid(nx, ny):
            continue
        myd = md(nx, ny, tx, ty)
        oppd = md(ox, oy, tx, ty)

        # Small lookahead: if opponent is already closer to some resource, we avoid
        # moves that reduce our advantage.
        contested_pen = 0
        for r in resources:
            if not r or len(r) < 2:
                continue
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            my2 = md(nx, ny, rx, ry)
            op2 = md(ox, oy, rx, ry)
            # Penalize stepping into being worse on a resource that is within reach.
            if op2 + 0 < my2 and my2 <= 6:
                contested_pen += (my2 - op2)

        # Primary: reduce our distance; secondary: keep our edge over opponent.
        val = (-myd * 5) + (oppd - myd) * 2 - contested_pen * 1 - md(nx, ny, cx, cy) * 0.1
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if int(dx) not in (-1, 0, 1) or int(dy) not in (-1, 0, 1):
        return [0, 0]
    return [int(dx), int(dy)]