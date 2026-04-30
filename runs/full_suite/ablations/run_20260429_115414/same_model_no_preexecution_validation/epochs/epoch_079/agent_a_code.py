def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        tx, ty = (w - 1 if sx < ox else 0), (h - 1 if sy < oy else 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    # Greedy 2-ply: choose our move that maximizes chance to arrive first.
    # Also: prefer moving away from opponent when ties exist; and avoid positions adjacent to obstacles.
    res_sorted = sorted(resources, key=lambda p: (p[0] * 9 + p[1]))  # deterministic tie base
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        score = 0.0
        # Obstacle adjacency penalty (discourage risky lanes).
        adj = 0
        for ax, ay in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            px, py = nx + ax, ny + ay
            if (px, py) in obstacles:
                adj += 1
        score -= 0.18 * adj

        # Evaluate best target after this move
        local_best = None
        for rx, ry in res_sorted:
            d_me1 = cheb(nx, ny, rx, ry)
            d_op1 = cheb(ox, oy, rx, ry)
            # If opponent is already closer, heavily penalize.
            ahead = d_op1 - d_me1
            # Tie-break toward targets closer to our corner (but different from opponent).
            corner_bias = (abs(rx - (0 if sx > (w - 1) // 2 else (w - 1))) + abs(ry - (0 if sy > (h - 1) // 2 else (h - 1)))) * 0.002
            # Prefer reducing chebyshev distance to the chosen resource.
            local = ahead - 0.05 * (d_me1) + 0.02 * (abs(rx - nx) + abs(ry - ny)) * -0.01 - corner_bias
            if local_best is None or local > local_best:
                local_best = local
        score += (local_best if local_best is not None else -999.0)

        # Second ply: simulate our next step toward the same move target by favoring lower min distance
        # to resources from next position (cheap). Also small anti-opponent movement if near a resource.
        min_d = None
        for rx, ry in res_sorted:
            d = cheb(nx, ny, rx, ry)
            if min_d is None or d < min_d:
                min_d = d
        score -= 0.06 * (min_d if min_d is not None else 0)
        score += 0.03 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))  # slightly keep distance from