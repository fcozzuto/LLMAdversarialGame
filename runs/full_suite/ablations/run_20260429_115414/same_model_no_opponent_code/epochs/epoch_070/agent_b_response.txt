def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_val = -10**18
    best_move = (0, 0)

    if not resources:
        tx, ty = cx, cy
        # step toward center deterministically
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in deltas:
            nx, ny = sx + mx, sy + my
            if valid(nx, ny):
                return [mx, my]
        return [0, 0]

    for mx, my in deltas:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        min_ds = 10**9
        min_do = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            if ds < min_ds:
                min_ds = ds
            do = man(ox, oy, rx, ry)
            if do < min_do:
                min_do = do
        # Prefer stealing: where self is closer than opponent; also prefer shorter self distance.
        # Small penalty if moving toward opponent to reduce collisions being unproductive.
        v = (min_do - min_ds) * 120 - min_ds * 3
        v -= (man(nx, ny, ox, oy) * 0.2)
        if min_ds == 0:
            v += 10000
        if v > best_val:
            best_val = v
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]