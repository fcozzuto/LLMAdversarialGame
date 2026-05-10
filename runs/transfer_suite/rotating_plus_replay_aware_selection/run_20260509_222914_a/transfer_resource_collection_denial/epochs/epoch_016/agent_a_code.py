def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def man(ax, ay, bx, by):
        ax -= bx
        ay -= by
        if ax < 0: ax = -ax
        if ay < 0: ay = -ay
        return ax + ay

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        if inb(x + dx, y): return [dx, 0] if dy == 0 else [dx, dy]
        if inb(x, y + dy): return [0, dy] if dx == 0 else [dx, dy]
        return [0, 0]

    # Deterministic tie-break order preference when scores equal.
    move_order = {(-1, 0): 0, (1, 0): 1, (0, -1): 2, (0, 1): 3, (-1, -1): 4, (1, -1): 5, (-1, 1): 6, (1, 1): 7, (0, 0): 8}

    best_score = -10**18
    best_move = [0, 0]

    for dx0, dy0 in deltas:
        nx, ny = x + dx0, y + dy0
        if not inb(nx, ny):
            continue

        # Resource-denier heuristic: maximize our advantage on the single best target,
        # while slightly preferring being closer to prevent opponent sniping.
        best_gap = -10**18
        best_sd = 10**9
        for rx, ry in resources:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            gap = od - sd  # positive => we are closer this turn
            if gap > best_gap:
                best_gap = gap
            if sd < best_sd:
                best_sd = sd

        # If we are behind everywhere, still minimize distance to the nearest resource.
        # Scale to keep gap dominant but responsive when gap ties.
        score = best_gap * 1000 - best_sd

        if score > best_score:
            best_score = score
            best_move = [dx0, dy0]
        elif score == best_score:
            if move_order[(dx0, dy0)] < move_order[(best_move[0], best_move[1])]:
                best_move = [dx0, dy0]

    return [int(best_move[0]), int(best_move[1])]