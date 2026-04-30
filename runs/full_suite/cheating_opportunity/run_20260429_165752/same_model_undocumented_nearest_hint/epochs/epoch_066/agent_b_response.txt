def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            val = (d, -cheb(nx, ny, W - 1, H - 1), -dx * dx - dy * dy)
            if best is None or val > best:
                best = val
                best_move = [dx, dy]
        return best_move

    # Choose a contested target: prefer resources where we can arrive earlier than opponent.
    best_target = None
    best_tval = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Higher is better: (opponent is farther) and myd small; slight preference toward center-ish to reduce being boxed.
        center_bias = - (abs(rx - (W - 1) / 2) + abs(ry - (H - 1) / 2)) * 0.01
        val = (opd - myd, -myd, center_bias)
        if best_tval is None or val > best_tval:
            best_tval = val
            best_target = (rx, ry)

    tr, ty = best_target
    best_move = [0, 0]
    best_mval = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, tr, ty)
        opd2 = cheb(ox, oy, tr, ty)
        # Move to reduce our distance to target; also keep opponent from benefiting by favoring moves that keep us ahead.
        ahead = opd2 - myd2
        separation = cheb(nx, ny, ox, oy)
        val = (ahead, -myd2, separation, -dx * dx - dy * dy)
        if best_mval is None or val > best_mval:
            best_mval = val
            best_move = [dx, dy]
    return best_move