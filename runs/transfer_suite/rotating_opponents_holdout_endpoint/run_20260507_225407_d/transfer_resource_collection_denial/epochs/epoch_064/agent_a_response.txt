def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            x, y = p
            x, y = int(x), int(y)
            if inb(x, y):
                obs.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    res_list = observation.get("resources") or []
    resources = []
    for p in res_list:
        try:
            x, y = p
            x, y = int(x), int(y)
            if ok(x, y):
                resources.append((x, y))
        except Exception:
            pass

    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if not ok(sx, sy) or not resources:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if ok(nx, ny) and (dx != 0 or dy != 0):
                    return [dx, dy]
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Choose resource we can reach sooner (denier tries to steal; we prioritize advantage).
    best = None
    best_cmp = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        advantage = od - sd
        # Prefer positive advantage, then smaller sd, then closer to us-farther-from-opponent.
        cmp = (advantage, -sd, advantage - od)
        if best is None or cmp > best_cmp:
            best, best_cmp = (rx, ry), cmp

    tx, ty = best
    # Greedy one-step move towards target, but keep it safe and maintain advantage.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            sd2 = md(nx, ny, tx, ty)
            od2 = md(ox, oy, tx, ty)
            adv2 = od2 - sd2
            # Small nudge to deter standing still while not necessary.
            candidates.append((adv2, -sd2, -(abs(dx) + abs(dy)), dx, dy))
    candidates.sort(reverse=True)
    return [int(candidates[0][3]), int(candidates[0][4])] if candidates else [0, 0]