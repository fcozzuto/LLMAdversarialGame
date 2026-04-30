def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        # No resources: move to mirror opponent direction while staying safe
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny):
                return [ddx, ddy]
        return [0, 0]

    best_us = None  # (adv, rd, rx, ry)
    best_opp = None  # (adv, rd, rx, ry)
    for rx, ry in resources:
        rd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - rd  # positive means we are closer
        # Prefer resources we are closer to for "go"
        key_us = (adv, -rd, rx, ry)
        if best_us is None or key_us > best_us:
            best_us = key_us
        # Prefer resources opponent is closer to for "deny"
        key_opp = (-adv, -od, rx, ry)  # smaller (-adv) => us far; we want deny strongest
        if best_opp is None or key_opp > best_opp:
            best_opp = key_opp

    # Decide mode: Go for ours if we can be meaningfully closer; else deny opponent's best target.
    rxg, ryg = best_us[2], best_us[3]
    rxd, ryd = best_opp[2], best_opp[3]
    rdg = man(sx, sy, rxg, ryg)
    odd = man(ox, oy, rxd, ryd)
    odg = man(ox, oy, rxg, ryg)
    mode_target = (rxg, ryg) if (odg - rdg) >= 1 else (rxd, ryd)

    tx, ty = mode_target

    # Evaluate candidate moves: race toward target, and in deny mode, also reduce opponent's approach
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_cur = man(sx, sy, tx, ty)
        # If in go mode, reward reducing our distance; if in deny mode, reward increasing opponent distance
        d_opp_to = man(ox, oy, tx, ty)
        d_opp_from_new = man(nx, ny, ox, oy)
        improvement = d_cur - d_self

        score = improvement * 20 - d_self
        # Obstacle-aware "lane" pressure: don't drift away from target
        score += (-1 if (tx == sx and dx == 0) else 0) * 0
        if (odg - rdg)