def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def eval_pos(x, y):
        if resources:
            best = -10**9
            for rx, ry in resources:
                d_me = cheb(x, y, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                # Prefer resources we are strictly closer to; break ties deterministically with a small bias.
                gain = 100 - d_me * 3
                if d_me < d_op:
                    gain += 20
                elif d_me == d_op:
                    gain -= 5
                # Encourage reducing distance while discouraging "chasing" an equally-close opponent.
                gain -= (d_op - d_me) * 2
                if gain > best:
                    best = gain
            target_score = best
        else:
            target_score = -cheb(x, y, ox, oy)  # fall back: drift away from opponent

        # Opponent distance pressure (avoid getting too close unless it helps resources)
        opp_dist = cheb(x, y, ox, oy)
        safety = (opp_dist - 1) * 2

        # Mild preference to keep moving (avoid endless stay if alternatives exist)
        stay_pen = -2 if (x == sx and y == sy) else 0
        return target_score + safety + stay_pen

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic tie-breaking order: dirs already fixed
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move