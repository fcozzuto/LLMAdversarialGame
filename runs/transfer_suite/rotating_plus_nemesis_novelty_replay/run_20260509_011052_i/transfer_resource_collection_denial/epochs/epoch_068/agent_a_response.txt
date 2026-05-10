def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_winning = None
    best_win_key = None
    best_denial = None
    best_denial_key = None

    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd  # positive => we can reach no later than opponent
        # Winning: maximize how much earlier we are; break ties by shorter self distance; then prefer nearer to center.
        win_key = (adv, -sd, -abs(rx - (w - 1) / 2.0) - abs(ry - (h - 1) / 2.0), -rx, -ry)
        if best_win_key is None or win_key > best_win_key:
            best_win_key = win_key
            best_winning = (rx, ry)

        # Denial: if we can't win, target what opponent is closest to (min od),
        # and also keep our distance relatively small to potentially contest.
        denial_key = ( -od, sd, abs(od - sd), -rx, -ry )
        if best_denial_key is None or denial_key > best_denial_key:
            best_denial_key = denial_key
            best_denial = (rx, ry)

    rx, ry = best_winning
    sd = cheb(sx, sy, rx, ry)
    od = cheb(ox, oy, rx, ry)
    if od <= sd:
        rx, ry = best_denial

    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
        return [dx, dy]

    # If blocked or invalid, try axis-aligned deterministic fallback.
    if 0 <= sx + dx < w and (sx + dx, sy) not in blocked:
        return [dx, 0]
    if 0 <= sy + dy < h and (sx, sy + dy) not in blocked:
        return [0, dy]
    return [0, 0]