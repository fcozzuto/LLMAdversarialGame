def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    def get_xy(v, default=(0, 0)):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return (int(v[0]), int(v[1]))
        return default

    sx, sy = get_xy(observation.get("self_position", (0, 0)))
    ox, oy = get_xy(observation.get("opponent_position", (sx, sy)))

    obs = set()
    for o in observation.get("obstacles", []) or []:
        x, y = get_xy(o, None)
        if x is None:
            continue
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in observation.get("resources", []) or []:
        x, y = get_xy(r, None)
        if x is None:
            continue
        if free(x, y):
            resources.append((x, y))

    if not resources:
        return [0, 0]

    opp_d = lambda x, y: abs(x - ox) + abs(y - oy)
    self_d = lambda x, y: abs(x - sx) + abs(y - sy)

    def best_target(px, py):
        # Prefer a resource where opponent arrives later than we do; break ties by closer to us.
        bx, by = resources[0]
        best = (-10**9, 10**9)
        for x, y in resources:
            sd = abs(x - px) + abs(y - py)
            od = abs(x - ox) + abs(y - oy)
            key = (od - sd, sd)
            if key > best:
                best = key
                bx, by = x, y
        return bx, by

    tx, ty = best_target(sx, sy)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_move = (0, 0, -10**9, 10**9)
    for dx, dy, nx, ny in moves:
        bx, by = best_target(nx, ny)
        sd = abs(bx - nx) + abs(by - ny)
        od = abs(bx - ox) + abs(by - oy)
        key = (od - sd, -sd)  # maximize (od-sd); then smaller sd
        if key[0] > best_move[2] or (key[0] == best_move[2] and key[1] > best_move[3]):
            best_move = (dx, dy, key[0], key[1])

    return [int(best_move[0]), int(best_move[1])]