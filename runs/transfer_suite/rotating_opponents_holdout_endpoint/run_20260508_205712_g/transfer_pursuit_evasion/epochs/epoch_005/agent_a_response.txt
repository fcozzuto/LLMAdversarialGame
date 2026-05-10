def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs_set = {(int(a[0]), int(a[1])) for a in obstacles if isinstance(a, (list, tuple)) and len(a) >= 2}

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs_set

    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("run" in role) or ("esc" in role)
    is_pursuer = ("purs" in role) or ("catch" in role) or ("pred" in role)
    if not is_evader and not is_pursuer:
        is_evader = False  # default: pursuer

    def mobility(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    best = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        dist2 = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        mob = mobility(nx, ny)
        if is_evader:
            val = (dist2, mob, -abs(nx - (w - 1 - ox)) - abs(ny - (h - 1 - oy)))
            better = (best_val is None) or (val > best_val)
        else:
            val = (-dist2, mob, -abs(nx - ox) - abs(ny - oy))
            better = (best_val is None) or (val > best_val)
        if better:
            best_val = val
            best = [dx, dy]
    return best if best is not None else [0, 0]