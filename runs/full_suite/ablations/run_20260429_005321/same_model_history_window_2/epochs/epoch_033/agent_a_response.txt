def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        best = (0, 0)
        bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            k = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate this move by the best target it can reach "effectively"
        best_val = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            block = 0.0
            if opd < myd:
                block = 1.5  # don't chase resources opponent is currently closer to
            # Prefer resources closer to me, farther from opponent, and towards center slightly
            val = myd - 0.25 * opd + block + 0.05 * (abs(rx - cx) + abs(ry - cy))
            if best_val is None or val < best_val:
                best_val = val

        # Secondary objective: reduce distance to current chosen best target area and avoid giving opponent shortcuts
        opp_to_me = cheb(ox, oy, nx, ny)
        my_center = abs(nx - cx) + abs(ny - cy)
        key = (best_val, my_center, opp_to_me, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]