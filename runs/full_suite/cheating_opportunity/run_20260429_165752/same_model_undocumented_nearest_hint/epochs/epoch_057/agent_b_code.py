def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        tx, ty = (W // 2), (H // 2)
        resources = [(tx, ty)]

    # Pick a target resource that we are relatively more likely to secure than the opponent.
    best_target = resources[0]
    best_m = 10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        m = myd - 0.9 * opd
        if m < best_m:
            best_m = m
            best_target = (rx, ry)
    rx0, ry0 = best_target

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Re-evaluate locally for this move to adapt if another resource becomes better.
        chosen_rx, chosen_ry = rx0, ry0
        chosen_m = 10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            m = myd - 0.9 * opd
            if m < chosen_m:
                chosen_m = m
                chosen_rx, chosen_ry = rx, ry

        my_to = cheb(nx, ny, chosen_rx, chosen_ry)
        opp_to = cheb(ox, oy, chosen_rx, chosen_ry)
        opp_dist_me = cheb(nx, ny, ox, oy)

        # Prefer securing likely resource (high myd/opd advantage), being close to it, and not allowing opponent proximity.
        score = (-0.7 * my_to) + (0.8 * (opp_to - my_to)) + (0.15 * opp_dist_me)
        # Small tie-break: move toward center-ish to avoid dead areas.
        cx, cy = W // 2, H // 2
        score += -0.02 * cheb(nx, ny, cx, cy)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]