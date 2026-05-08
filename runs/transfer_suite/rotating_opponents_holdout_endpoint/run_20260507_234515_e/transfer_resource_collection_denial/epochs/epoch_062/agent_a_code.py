def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = (-1, 0, 1)
    best_score = -10**18
    best_move = (0, 0)

    # Greedy one-step lookahead: pick the move that maximizes "capture advantage" over all resources.
    # Advantage is positive when we are closer than opponent; add urgency when turns run low.
    urgency = 1.0 + (0.0 if turns_remaining is None else max(0, 64 - int(turns_remaining))) / 64.0

    for dx in dirs:
        for dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            move_score = -10**18
            for tx, ty in res:
                sd = man((nx, ny), (tx, ty))
                od = man((ox, oy), (tx, ty))
                # If immediate collection available, heavily prefer it.
                if sd == 0:
                    score = 10**9
                else:
                    # Prefer states where we can arrive earlier/equal than opponent.
                    delta = (od - sd)
                    # Slightly prefer closer overall to reduce stalling.
                    score = (delta * 1000.0) - (sd * 2.0) + (delta * delta) * 0.1
                    score *= urgency
                if score > move_score:
                    move_score = score
            if move_score > best_score:
                best_score = move_score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]