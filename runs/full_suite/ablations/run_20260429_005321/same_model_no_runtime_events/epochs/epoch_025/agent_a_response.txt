def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    res_set = set()
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
                res_set.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = -10**18
    opp_dist_now = cheb(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        # Targeting: closest resource, but prefer states where we beat opponent to it.
        if resources:
            score_to = 0
            min_adv = 10**9
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                adv = d_op - d_me  # positive => we are closer
                if adv < min_adv:
                    min_adv = adv
            # Encourage moving toward the best "beat-opponent" resource.
            # Also encourage overall closeness to any resource.
            d_any = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score_to = 40 * min_adv - 3 * d_any
        else:
            # No visible resources: drift to center-ish to reduce wasted movement
            score_to = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))

        # Immediate collection bonus
        collect_bonus = 120 if (nx, ny) in res_set else 0

        # Defensive/denial: avoid letting opponent approach too much; mildly prefer increasing their distance
        opp_dist_next = cheb(nx, ny, ox, oy)
        opp_penalty = -6 * max(0, opp_dist_now - opp_dist_next) - 2 * (opp_dist_next == 0)

        # If opponent is adjacent, bias toward moving away
        away_bias = 0
        if cheb(nx, ny, ox, oy) <= 1:
            away_bias = 25 * (cheb(nx, ny, sx, sy) + 1)  # deterministic, still prefers stepping away

        # Combine
        score = collect_bonus + score_to + opp_penalty + away_bias

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]