def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            key = (opp_d - our_d, -our_d, rx, ry)  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key, best = key, (rx, ry)
        tx, ty = best
    else:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0

    dx0 = 0
    dy0 = 0
    if isinstance(tx, int):
        dx0 = 0 if tx == sx else (1 if tx > sx else -1)
        dy0 = 0 if ty == sy else (1 if ty > sy else -1)
    else:
        txm = int(tx + 0.5)
        tym = int(ty + 0.5)
        dx0 = 0 if txm == sx else (1 if txm > sx else -1)
        dy0 = 0 if tym == sy else (1 if tym > sy else -1)

    target_hint = (dx0, dy0)
    ordered = sorted(moves, key=lambda m: (0 if m == target_hint else 1, m[0], m[1]))

    best_move = (0, 0)
    best_val = None
    for mdx, mdy in ordered:
        nx, ny = sx + mdx, sy + mdy
        if not in_bounds(nx, ny):
            continue
        if resources:
            our_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            val = (opp_d - our_d, -our_d)
        else:
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            d1 = abs(nx - cx) + abs(ny - cy)
            val = (-d1, 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]