def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def man(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da + db

    targets = []
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        adv = od - sd
        targets.append((adv, sd, od, rx, ry))
    if not targets:
        return [0, 0]
    targets.sort(reverse=True)
    _, _, _, tx, ty = targets[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        nod = man(ox, oy, tx, ty)
        adv = nod - ns
        t = (adv, -ns, nod, tx, ty, dx, dy)
        if best is None or t > best:
            best = t
    if best is None:
        return [0, 0]
    dx, dy = best[-2], best[-1]
    return [int(dx), int(dy)]