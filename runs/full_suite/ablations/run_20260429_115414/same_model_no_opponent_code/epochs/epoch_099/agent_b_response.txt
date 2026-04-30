def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
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

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = kdist(nx, ny, cx, cy)
            cand = (d, dx, dy)
            if best is None or cand < best:
                best = cand
        return [int(best[1]), int(best[2])] if best else [0, 0]

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        opp_range = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)
        near_pen = -6 if opp_range else 0

        # Choose target resource where our advantage over opponent is largest
        best_target_score = -10**18
        for rx, ry in resources:
            myd = kdist(nx, ny, rx, ry)
            opd = kdist(ox, oy, rx, ry)
            # Prefer closer, and strongly prefer resources opponent is not closer to
            adv = (opd - myd)
            # Secondary: keep paths away from obstacles by small center bias and edge deterrence
            center_bias = -0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
            # Also slightly prefer immediate pickup (myd==0)
            pick_bonus = 3 if myd == 0 else 0
            val = adv * 2.0 + center_bias + pick_bonus - (1 if (rx, ry) == (ox, oy) else 0)
            if val > best_target_score:
                best_target_score = val

        # Avoid committing too directly into opponent while maximizing advantage
        total = best_target_score + near_pen - 0.15 * kdist(nx, ny, ox, oy)
        if total > best_score:
            best_score = total
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]