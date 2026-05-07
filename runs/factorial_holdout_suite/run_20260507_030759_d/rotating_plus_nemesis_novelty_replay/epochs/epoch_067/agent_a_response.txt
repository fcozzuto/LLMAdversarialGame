def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Interception-aware greedy: prefer resources we can reach earlier than opponent.
    t = int(observation.get("turn_index", 0) or 0)
    w_op = 4 if (t % 2 == 0) else 3  # small deterministic adaptation
    prefer_close = 1 if (t % 3 == 0) else 2

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate move by best achievable resource.
        move_val = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            # Reach advantage first, then urgency (shorter distance).
            adv = d_op - d_me
            urgency = -d_me
            value = w_op * adv + prefer_close * urgency
            if value > move_val:
                move_val = value
        # Tie-break deterministically: prefer staying near current best direction toward closest resource.
        if move_val > best_val:
            best_val = move_val
            best = [dx, dy]
        elif move_val == best_val:
            # Deterministic secondary: minimal distance to nearest resource from the candidate position
            cur_near = None
            cand_near = None
            # compute for current best
            bx, by = sx + best[0], sy + best[1]
            for rx, ry in resources:
                d = cheb(bx, by, rx, ry)
                if cur_near is None or d < cur_near:
                    cur_near = d
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if cand_near is None or d < cand_near:
                    cand_near = d
            if cand_near is not None and (cur_near is None or cand_near < cur_near):
                best = [dx, dy]

    return [int(best[0]), int(best[1])]