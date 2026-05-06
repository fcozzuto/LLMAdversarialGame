def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Estimate opponent's likely nearest target
    best_opp = None
    best_opp_d = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp = (rx, ry)

    target = best_opp if best_opp is not None else resources[0]
    tx, ty = target

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Base: try to improve ability to reach some resource first
        score = 0
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            if myd == 0:
                val = 10**9
            else:
                val = (opd - myd) * 120 - myd * 2
            # Slightly prefer resources that are on/near opponent target line
            if (rx == tx and abs(ry - ty) <= 2) or (ry == ty and abs(rx - tx) <= 2):
                val += 25
            score += val

        # Strategic change: if opponent is already close to their target, actively deny by chasing it
        deny_d = man(nx, ny, tx, ty)
        opp_d_after = man(ox, oy, tx, ty)
        if opp_d_after <= 3:
            score += 2000 - deny_d * 50

        # Tie-breaker: closer to our chosen target to reduce dithering
        score -= man(nx, ny, tx, ty) * 3

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]