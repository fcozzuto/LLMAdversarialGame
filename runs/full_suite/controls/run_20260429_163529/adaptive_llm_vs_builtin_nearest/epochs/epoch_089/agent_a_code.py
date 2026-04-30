def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp1(v):
        if v > 0: return 1
        if v < 0: return -1
        return 0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18
    ti = int(observation.get("turn_index", 0))

    # Consider only a few closest resources to keep deterministic and fast
    res_rank = sorted(resources, key=lambda r: (cheb(sx, sy, r[0], r[1]), r[0], r[1]))
    top_res = res_rank[:6]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Distance to opponent (prefer increasing it slightly)
        opp_d = cheb(nx, ny, ox, oy)

        # Choose a target via "likely contest": prefer resources where we are at least as close as opponent
        s_best = -10**18
        for rx, ry in top_res:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            # If opponent is closer to the same resource, penalize
            contest = 0 if my_d <= op_d else (my_d - op_d)
            # Bias toward capturing sooner and staying away from opponent
            score = -my_d - 2.0 * contest + 0.15 * opp_d
            # Tiny deterministic tie-break
            score -= 0.001 * (abs(rx - ox) + abs(ry - oy)) + 0.0001 * (rx * 8 + ry)
            if score > s_best:
                s_best = score

        # Deterministic tie-break using move order and turn parity
        score = s_best + (0.00001 * (dx + 2 * dy)) + (0.000001 * ((ti % 2) * (dx - dy)))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]