def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        return [0, 0]

    opp_best = None
    opp_best_d = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        d = dist((ox, oy), (rx, ry))
        if opp_best_d is None or d < opp_best_d or (d == opp_best_d and (rx, ry) < opp_best):
            opp_best_d = d
            opp_best = (rx, ry)

    self_best_adv = None
    self_best_adv_key = None
    for rx, ry in resources:
        if (rx, ry) in obs:
            continue
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        adv = od - sd
        key = (-(adv), sd, (rx, ry))  # minimize sd when adv equal; maximize adv overall via negative
        if self_best_adv_key is None or key < self_best_adv_key:
            self_best_adv_key = key
            self_best_adv = (rx, ry)

    # If opponent is closer to its nearest target, race it (deny). Otherwise chase best advantage.
    target = opp_best if opp_best is not None and dist((sx, sy), opp_best) >= (opp_best_d if opp_best_d is not None else 10**9) else self_best_adv
    if target is None:
        return [0, 0]
    tx, ty = target

    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Prefer reducing distance to target; if racing, also reduce the gap to opponent's nearest target.
        d_self = dist((nx, ny), (tx, ty))
        if opp_best is not None:
            d_opp_target = dist((ox, oy), opp_best)
            gap_before = dist((sx, sy), opp_best) - d_opp_target
            gap_after = d_self - d_opp_target
            score = (gap_after, d_self, -dx, -dy) if (target == opp_best) else (d_self, abs(tx - nx) + abs(ty - ny), -dx, -dy)
        else:
            score = (d_self, abs(tx - nx) + abs(ty - ny), -dx, -dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]