def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = w // 2, h // 2
        best_step = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            k = (cheb(nx, ny, tx, ty), cheb(ox, oy, tx, ty), nx, ny)
            if best_step is None or k < best_step[0]:
                best_step = (k, [dx, dy])
        return best_step[1] if best_step else [0, 0]

    best_key = None
    best_target = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # New priority: secure resources we are more likely to reach first; if not, pick the one that blocks opponent best.
        # Key: (win_prob, my_time, opp_time, tiebreak coords)
        win_prob = 0 if myd <= opd else 1
        key = (win_prob, myd, -opd, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_target = key, (rx, ry)

    tx, ty = best_target
    # Greedy one-step with deterministic tie-break; avoid stepping into obstacles.
    best_step = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        win_prob = 0 if myd <= opd else 1
        key = (win_prob, myd, -opd, nx, ny)
        if best_step is None or key < best_step[0]:
            best_step = (key, [dx, dy])
    return best_step[1] if best_step else [0, 0]