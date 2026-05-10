def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

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

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def key(cell):
        rx, ry = cell
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        # Prefer winning race (positive margin), then earlier arrival, then deterministic tie-break
        margin = opp_d - my_d
        return (margin, -my_d, -rx, -ry)

    # Opponent's apparent nearest target (to reduce collisions)
    opp_target = None
    opp_best = None
    for rx, ry in resources:
        d = cheb(ox, oy, rx, ry)
        k = (-d, -rx, -ry)
        if opp_best is None or k > opp_best:
            opp_best = k
            opp_target = (rx, ry)

    # If we can beat the likely opponent target, go there; else choose best non-colliding target.
    if opp_target in resources:
        rx, ry = opp_target
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        if my_d <= opp_d:
            target = opp_target
        else:
            best = None
            bestk = None
            for cell in resources:
                if cell == opp_target:
                    continue
                k = key(cell)
                if bestk is None or k > bestk:
                    bestk = k
                    best = cell
            target = best if best is not None else opp_target
    else:
        target = max(resources, key=key)

    tx, ty = target
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    return [dx, dy]