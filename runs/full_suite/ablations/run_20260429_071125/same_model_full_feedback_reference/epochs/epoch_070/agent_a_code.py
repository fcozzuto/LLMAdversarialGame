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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best = None
        best_score = -10**18
        for rx, ry in resources:
            our_d = cheb(sx, sy, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we can beat; also prefer shorter paths once we do.
            score = (opp_d - our_d) * 4 - our_d
            if score > best_score:
                best_score = score
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_key = (-10**18, -10**18, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        # Move to reduce our distance to the target; if equal, increase the beat-margin.
        our_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, tx, ty)
        key1 = -our_d
        key2 = (opp_d - our_d)
        # Slight bias to not drift too far from center early.
        cx, cy = w // 2, h // 2
        key3 = -cheb(nx, ny, cx, cy)
        if (key1, key2, key3) > best_key:
            best_key = (key1, key2, key3)
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]