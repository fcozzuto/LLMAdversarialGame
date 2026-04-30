def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_score = None
        for rx, ry in resources:
            d_me = cheb(sx, sy, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            score = (d_op - d_me, -d_me, rx, ry)  # maximize advantage, then closer to self, then deterministic
            if best_score is None or score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
        # Prefer moves that get us closer; if tied, reduce opponent distance too.
        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dme2 = cheb(nx, ny, tx, ty)
            dop2 = cheb(ox, oy, tx, ty)
            # also slightly bias away from giving opponent immediate access by reducing distance between opponent and target
            key = (-dme2, dop2, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No visible resources: advance to reduce distance to opponent and improve coverage of center.
    tx, ty = (w // 2, h // 2)
    if cheb(sx, sy, ox, oy) <= cheb(sx, sy, tx, ty):
        tx, ty = ox, oy

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = (-cheb(nx, ny, tx, ty), cheb(nx, ny, ox, oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]