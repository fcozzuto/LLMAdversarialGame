def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        return [0, 0]

    # Choose a target where we are ahead if possible; otherwise minimize opponent lead.
    best_target = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        ahead = do - ds
        # Prefer positive ahead strongly; then closer; then deterministic.
        if ahead > 0:
            key = (-1, -ahead, ds, do, rx * 131 + ry * 17)
        else:
            key = (0, ahead, ds, do, rx * 131 + ry * 17)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    # Evaluate one-step moves (including diagonals), avoid obstacles if possible.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        # Heuristic: maximize our advantage (reduce ds relative to opponent) and progress to target.
        cur_do = man(ox, oy, tx, ty)
        adv = cur_do - ns  # higher is better
        # Additional small tie-break: avoid stepping away if possible.
        ds0 = man(sx, sy, tx, ty)
        progress = ds0 - ns
        key = (-adv, -progress, ns, dx * 3 + dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]