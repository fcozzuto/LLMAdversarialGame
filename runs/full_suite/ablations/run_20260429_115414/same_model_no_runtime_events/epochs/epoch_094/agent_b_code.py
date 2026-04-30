def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = sorted(moves)

    if not resources:
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = (-10**18, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            val = -(cheb(nx, ny, tx, ty)) - cheb(nx, ny, ox, oy) * 0.05
            if val > best[0]:
                best = (val, dx, dy)
        if best[1] or best[2]:
            return [best[1], best[2]]
        return [0, 0]

    best_val = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer targets where we are closer than opponent.
        val = 0
        near_obs_pen = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d <= 1:
                near_obs_pen -= 3
            elif d <= 2:
                near_obs_pen -= 1

        best_t = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Lead bonus strongly, then distance.
            lead = d_op - d_me
            # Avoid "giving up" where opponent is clearly closer.
            tval = lead * 6 - d_me
            # Small preference to central resources to reduce dead-ends.
            cx, cy = (w - 1) // 2, (h - 1) // 2
            tval -= 0.05 * cheb(rx, ry, cx, cy)
            if d_me == 0:
                tval += 1000
            best_t = tval if tval > best_t else best_t
        val = best_t + near_obs_pen
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]