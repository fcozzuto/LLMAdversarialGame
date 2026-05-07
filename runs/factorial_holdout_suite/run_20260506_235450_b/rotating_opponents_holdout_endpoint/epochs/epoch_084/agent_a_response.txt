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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -sd, tx, ty)  # deterministic
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx_options = (-1, 0, 1)
    dy_options = (-1, 0, 1)

    best_move = (0, 0)
    best_move_key = None
    for dx in dx_options:
        for dy in dy_options:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obs_set:
                continue
            nd = man(nx, ny, tx, ty)
            # Also discourage stepping closer for opponent to the same target
            nod = man(ox, oy, tx, ty)
            move_key = (-nd, -abs((nx + ny) - (tx + ty)), -nod, dx, dy)
            if best_move_key is None or move_key > best_move_key:
                best_move_key = move_key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]