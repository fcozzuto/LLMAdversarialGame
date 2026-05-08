def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    for r in resources:
        if r[0] == sx and r[1] == sy:
            return [0, 0]

    if not resources:
        tx, ty = w - 1, 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        for ddy in (-1, 0, 1):
            for ddx in (-1, 0, 1):
                nx, ny = sx + ddx, sy + ddy
                if inb(nx, ny) and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [0, 0]

    best = None
    best_tuple = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        adv = od - sd  # positive means we are closer
        # Prefer guaranteed grabs: only consider adv>=0, otherwise still pick best-but-lose if forced.
        t = (-(1 if adv >= 0 else 0), -adv, sd, rx, ry)
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best = (rx, ry)

    tx, ty = best
    options = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    cand = []
    for dx, dy in options:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            sd2 = abs(tx - nx) + abs(ty - ny)
            od2 = abs(tx - ox) + abs(ty - oy)
            adv2 = od2 - sd2
            # Greedy toward improving advantage; slight preference to reduce distance when equal.
            cand.append(((0 if adv2 >= 0 else 1), -adv2, sd2, nx, ny, dx, dy))
    cand.sort()
    return [cand[0][5], cand[0][6]] if cand else [0, 0]