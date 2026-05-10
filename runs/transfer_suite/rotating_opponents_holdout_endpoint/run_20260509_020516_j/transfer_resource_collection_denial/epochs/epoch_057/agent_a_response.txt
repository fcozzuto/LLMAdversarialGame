def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Predict opponent's likely target (nearest-resource style but relative to us)
    best_t = resources[0]
    best_k = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        k = (sd - od, -od, -(sd + od), -abs(rx - ox) - abs(ry - oy))
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    opp_tx, opp_ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate the best contestable resource from this next position
        local_best = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Encourage stealing the opponent's likely target, but only if we can compete
            steal = 80 if (rx == opp_tx and ry == opp_ty) else 0
            val = (od - sd) * 100 - sd + steal
            if local_best is None or val > local_best:
                local_best = val

        # Slight preference for moves that reduce distance to the opponent's target
        tie_boost = -cheb(nx, ny, opp_tx, opp_ty)
        total = local_best * 1000 + tie_boost

        if best_val is None or total > best_val:
            best_val = total
            best_move = [dxm, dym]

    return best_move