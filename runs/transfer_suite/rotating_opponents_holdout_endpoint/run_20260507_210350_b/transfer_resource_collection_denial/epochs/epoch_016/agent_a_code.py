def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", []) if tuple(p) not in obstacles]
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (priority, sd, -adv, tie, tx, ty)

    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        contest = (sd <= od + 1)
        adv = od - sd
        tie = ((tx * 31 + ty * 17 + sd * 7 + od) % 97)
        cand = (0 if contest else 1, sd, -adv, tie, tx, ty)
        if best is None or cand < best:
            best = cand

    _, _, _, _, tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try direct move first, then best alternative that doesn't hit obstacles/outside.
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    desired = (sx + dx, sy + dy)
    if valid(desired[0], desired[1]):
        return [dx, dy]

    # Alternative: pick move minimizing (self_dist - opponent_dist) to the chosen target.
    best_move = (0, 0)
    best_key = None
    for mx, my in dirs:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        nsd = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        key = (nsd, -nod, mx * 3 + my * 5)  # deterministic tie
        if best_key is None or key < best_key:
            best_key = key
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]