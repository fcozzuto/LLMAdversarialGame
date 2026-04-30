def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        best = (-10**18, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            dcen = abs(nx - cx) + abs(ny - cy)
            dfar = cheb(nx, ny, ox, oy)
            score = int(dcen * 1000) * -1 + dfar
            if score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Evaluate the best resource we could contest after this move.
        best_move_score = -10**18
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            adv = opd - myd  # positive => we are closer
            score = 2000 * adv - 10 * myd - 3 * opd
            if score > best_move_score:
                best_move_score = score

        # Small tie-break: prefer increasing our distance from opponent if contest is similar.
        opp_gap = cheb(nx, ny, ox, oy)
        score2 = best_move_score + (opp_gap // 2)
        if score2 > best[0]:
            best = (score2, dx, dy)

    return [best[1], best[2]]