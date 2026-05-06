def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    if not resources:
        # Drift toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if sx < tx else -1)
        dy = 0 if sy == ty else (1 if sy < ty else -1)
        return [dx, dy]

    # Precompute opponent distances to resources
    opp_d = {}
    for rx, ry in resources:
        opp_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    # Evaluate one-step moves
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        score = 0
        min_us = 10**9
        # Prefer resources where we are ahead, otherwise those that reduce our lead
        for rx, ry in resources:
            us = cheb(nx, ny, rx, ry)
            d_adv = opp_d[(rx, ry)] - us  # positive means we are closer
            if d_adv > 0:
                score += 2000 + 10 * d_adv - us
            else:
                # Still consider moving toward likely contested resources
                score += -2 * us + 6 * d_adv

            if us < min_us:
                min_us = us

        # Small tie-breakers: avoid moving away from the closest resource; keep distance from opponent
        score += -2 * min_us + 0.5 * cheb(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]