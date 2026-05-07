def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < gw and 0 <= y < gh
    def legal(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in sorted(moves):
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Pick target resource with best advantage (my reach sooner, tie-break by closer to me and then position)
    best_t = None
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Higher is better; prefer myd<=opd, also prefer shorter myd
        score = (opd - myd) * 2 - myd
        # Deterministic tie-break
        if score > best_score or (score == best_score and (rx < best_t[0] or (rx == best_t[0] and ry < best_t[1]))):
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    cur_my = cheb(sx, sy, tx, ty)
    cur_op = cheb(ox, oy, tx, ty)

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in sorted(moves):
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        # Prefer immediate improvement; small penalty for moving away
        improve = cur_my - myd
        # If we can capture soon, value it; also discourage letting opponent become clearly faster
        future_adv = (cur_op - myd)  # positive means opponent still not closer than me-from-next
        obstacle_pressure = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                px, py = nx + ax, ny + ay
                if (px, py) in obstacles:
                    obstacle_pressure += 1
        val = improve * 5 + future_adv * 0.8 - obstacle_pressure * 0.05
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move