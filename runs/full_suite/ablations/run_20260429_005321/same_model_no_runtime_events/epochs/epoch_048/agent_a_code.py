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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = -10**9

    if not resources:
        return [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Value a move by how quickly we reach resources vs opponent and by capturing risk.
        cur_best = None
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; also prefer smaller distance for us.
            val = (d_op - d_me) * 3 - d_me
            # Bonus if it is immediately on a resource.
            if d_me == 0:
                val += 1000
            # Small tie-breaker to move toward center-ish.
            val -= abs(nx - (w - 1) / 2) * 0.01 + abs(ny - (h - 1) / 2) * 0.01
            if cur_best is None or val > cur_best[0]:
                cur_best = (val, rx, ry, d_me, d_op)

        # If multiple resources, keep best.
        val = cur_best[0]
        # Additional safety: avoid stepping into a cell that increases opponent's immediate access too much.
        # (Opponent is deterred when we reduce their advantage.)
        opp_best = None
        for rx, ry in resources:
            d_op_next = cheb(ox, oy, rx, ry)
            d_me_next = cheb(nx, ny, rx, ry)
            t = (d_op_next - d_me_next) * 3 - d_me_next
            if opp_best is None or t > opp_best:
                opp_best = t
        val += opp_best * 0.02

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]