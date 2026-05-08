def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obs_list if p and len(p) >= 2}
    resources = observation.get("resources") or []
    roles = (str(observation.get("self_role", "")) + " " + str(observation.get("opponent_role", ""))).lower()
    is_pursuer = ("pursuer" in roles) or ("evader" not in roles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def step_toward(tx, ty, curx, cury):
        dx = 0 if tx == curx else (1 if tx > curx else -1)
        dy = 0 if ty == cury else (1 if ty > cury else -1)
        return dx, dy

    targets = []
    for r in resources:
        if r and len(r) >= 2:
            targets.append((int(r[0]), int(r[1])))
    if targets:
        best = None
        bestd = None
        for tx, ty in targets:
            d = abs(tx - sx)
            e = abs(ty - sy)
            dd = d if d > e else e
            if bestd is None or dd < bestd or (dd == bestd and (tx, ty) < best):
                bestd = dd
                best = (tx, ty)
        tx, ty = best
        if is_pursuer:
            dx, dy = step_toward(tx, ty, sx, sy)
        else:
            dx1, dy1 = step_toward(tx, ty, sx, sy)
            dx, dy = -dx1, -dy1
    else:
        dx1, dy1 = step_toward(ox, oy, sx, sy)
        if is_pursuer:
            dx, dy = dx1, dy1
        else:
            dx, dy = -dx1, -dy1

    nx, ny = sx + dx, sy + dy
    if inb(nx, ny):
        return [dx, dy]
    prefs = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0)]
    for a, b in prefs:
        nx, ny = sx + a, sy + b
        if a in (-1, 0, 1) and b in (-1, 0, 1) and inb(nx, ny):
            return [a, b]
    for a in (-1, 0, 1):
        for b in (-1, 0, 1):
            nx, ny = sx + a, sy + b
            if inb(nx, ny):
                return [a, b]
    return [0, 0]