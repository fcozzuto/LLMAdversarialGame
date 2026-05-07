def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except:
            continue
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            res.append((rx, ry, sd, od))
    if not res:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    best_adv = None
    ranked = []
    for rx, ry, sd, od in res:
        adv = od - sd
        if best_adv is None or adv > best_adv:
            best_adv = adv
        ranked.append((adv, -sd, -od, rx, ry, sd, od))

    if best_adv and best_adv > 0:
        ranked.sort(key=lambda t: (-(t[0]), t[1], t[2]))
        rx, ry, sd, od = ranked[0][3], ranked[0][4], ranked[0][5], ranked[0][6]
    else:
        # If behind everywhere, race the closest contested resource; favor smaller "worst-case" distance.
        ranked2 = []
        for rx, ry, sd, od in res:
            ranked2.append((-(sd if sd > od else od), -(sd - od), sd, od, rx, ry))
        ranked2.sort(key=lambda t: (t[0], t[1]))
        rx, ry, sd, od = ranked2[0][4], ranked2[0][5], ranked2[0][2], ranked2[0][3]

    # Anti-deny: if opponent is closer to target, bias toward the step that reduces our distance most.
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)
    if dx != 0 and dy != 0:
        # choose the component that gives best reduction against our distance metric deterministically
        candidates = [([dx, 0], cheb(sx + dx, sy, rx, ry)), ([0, dy], cheb(sx, sy + dy, rx, ry)), ([dx, dy], cheb(sx + dx, sy + dy, rx, ry))]
        candidates.sort(key=lambda c: (c[1], c[0][0], c[0][1]))
        return candidates[0][0]
    return [dx, dy]