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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    # If on a resource, secure it.
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    best_move = [0, 0]
    best_val = -10**18

    # One-step lookahead: pick move that maximizes (opponent disadvantage) on a best contested resource,
    # with tie-breakers pushing toward center and avoiding being too close to opponent.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_center = cheb(nx, ny, cx, cy)
        my_opp = cheb(nx, ny, ox, oy)
        # If opponent is very near, slightly penalize closeness to prevent clashes/teleports.
        opp_pen = my_opp if my_opp < 3 else 0

        if resources:
            best_contest = -10**18
            for rx, ry in resources:
                my_d = cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                # Prefer resources where we are closer than opponent; encourage taking over from them.
                contest = (op_d - my_d) * 100 - my_d
                # Slightly discourage moving toward resources behind obstacles clusters by preferring not-too-far from center.
                contest -= 2 * cheb(rx, ry, cx, cy)
                if contest > best_contest:
                    best_contest = contest
            val = best_contest - opp_pen - my_center
        else:
            # No visible resources: head to center.
            val = -my_center - opp_pen

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move