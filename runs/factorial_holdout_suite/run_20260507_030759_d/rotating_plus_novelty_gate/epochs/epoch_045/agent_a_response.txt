def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turns = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if (sx, sy) in obstacles or not legal:
        return [0, 0]

    if not resources:
        tx, ty = ((0, 0) if (sx + sy) % 2 == 0 else (w - 1, h - 1))
        best = None
        bestm = 10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            m = abs(tx - nx) + abs(ty - ny)
            if m < bestm:
                bestm = m
                best = (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    res = [tuple(r) for r in resources]
    if (sx, sy) in set(res):
        return [0, 0]

    best_target = None
    best_val = -10**18
    for rx, ry in res:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # Favor resources we can get before opponent; prefer closer and earlier
        v = (do - ds) * 1000 - ds
        if ds == 0:
            v = 10**12
        # Slightly adjust when time is tight
        if turns <= 8:
            v += (8 - ds) * 10
        if v > best_val:
            best_val = v
            best_target = (rx, ry)

    tx, ty = best_target
    best = (0, 0)
    bestm = 10**9
    bestd = -10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        m = abs(tx - nx) + abs(ty - ny)
        # Prefer strictly closer; else least distance; break ties by diagonal when useful
        d_self_gain = (abs(tx - sx) + abs(ty - sy)) - m
        diag = 1 if dx != 0 and dy != 0 else 0
        key_m = m
        key_d = d_self_gain * 2 + diag
        if key_m < bestm or (key_m == bestm and key_d > bestd):
            bestm = key_m
            bestd = key_d
            best = (dx, dy)
    return [int(best[0]), int(best[1])]