def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no visible resources, head toward the closest corner-center target to avoid oscillation
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny):
                nx, ny = sx, sy
            v = man(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                best = [dx if nx != sx else 0, dy if ny != sy else 0]
        return best if best is not None else [0, 0]

    # One-step lookahead scoring: prioritize reaching resources sooner while denying opponent access
    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        # our progress
        my_dist = 10**9
        for rx, ry in resources:
            d = man(nx, ny, rx, ry)
            if d < my_dist:
                my_dist = d

        # opponent threat: how close opponent is to the resource we would potentially contest
        opp_dist = 10**9
        for rx, ry in resources:
            d = man(ox, oy, rx, ry)
            if d < opp_dist:
                opp_dist = d

        # deny factor: prefer moves that make our advantage over opponent larger for nearby resources
        # (compare best resource distances from both agents)
        my_best = 10**9
        op_best = 10**9
        for rx, ry in resources:
            my_best = min(my_best, man(nx, ny, rx, ry))
            op_best = min(op_best, man(ox, oy, rx, ry))
        advantage = op_best - my_best

        # discourage moving toward opponent directly when not improving resource ETA
        to_op = man(nx, ny, ox, oy)

        score = (-my_best) + 0.9 * advantage - 0.02 * to_op - 0.005 * my_dist
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move