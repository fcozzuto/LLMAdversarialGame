def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        resources = [(w // 2, h // 2)]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Choose a contested target where we are closest relative to opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        md = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # maximize "our advantage"; tie-break by smaller our distance, then lexicographic
        key = (od - md, -md, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    my_d0 = cheb(sx, sy, tx, ty)
    op_d0 = cheb(ox, oy, tx, ty)

    # One-step lookahead: prioritize decreasing our distance and increasing opponent's distance to target.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d1 = cheb(nx, ny, tx, ty)
        # Approximate opponent response conservatively: assume they stay, evaluate their current distance.
        # To still "block", penalize moves that bring us close while opponent is already closer by a lot.
        op_d1_est = op_d0
        adv_gain = (op_d1_est - my_d1) - (op_d0 - my_d0)
        # Slightly prefer moves that reduce our distance even if already ahead.
        score = adv_gain * 10 + (my_d0 - my_d1) * 3 - (cheb(nx, ny, ox, oy) == 0) * 100
        # Deterministic tie-break
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]