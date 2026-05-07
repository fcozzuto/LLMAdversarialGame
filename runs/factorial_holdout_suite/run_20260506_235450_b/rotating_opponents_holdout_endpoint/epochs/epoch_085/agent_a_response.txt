def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            obs_set.add((int(ob[0]), int(ob[1])))

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd, -(tx + ty), tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (tx, ty)

    tx, ty = best_r
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    best_move = (0, 0)
    best_move_key = None
    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            hit = (nx, ny) in obs_set
            sd2 = man(nx, ny, tx, ty)
            opp2 = man(ox, oy, tx, ty)
            tie = (0 if hit else 1)
            key = (tie, -(sd2), (opp2 - sd2), -abs(tx - nx) - abs(ty - ny), -nx, -ny)
            if best_move_key is None or key > best_move_key:
                best_move_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]