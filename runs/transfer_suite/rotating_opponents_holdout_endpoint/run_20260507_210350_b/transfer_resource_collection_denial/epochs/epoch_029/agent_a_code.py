def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    turn = observation.get("turn_index", 0)

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        cx, cy = (w // 2, h // 2)
        if (sx + sy + turn) % 2:
            cx = 0 if cx > 0 else cx
        tx = cx if cx != sx else (w - 1 - cx)
        ty = cy if cy != sy else (h - 1 - cy)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        best_r_val = -10**18
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            if ds == 0:
                v = 10**6
            else:
                margin = do - ds
                share = (1 if rx == ox else 0) + (1 if ry == oy else 0)
                # Risk-averse: prioritize being closer (small ds) while still seeking positive margin
                v = margin * 120 - ds * 6 - share * 10
            if v > best_r_val:
                best_r_val = v
            elif v == best_r_val:
                if ds < man(nx, ny, rx, ry):
                    best_r_val = v

        # Prefer moves that improve our immediate prospects; tie-break toward smaller own distance to best target
        # Deterministic tie-break: compute a secondary metric directly for the best move
        sec = 10**9
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            margin = do - ds
            share = (1 if rx == ox else 0) + (1 if ry == oy else 0)
            v = (10**6 if ds == 0 else margin * 120 - ds * 6 - share * 10)
            if v == best_r_val and (ds < sec):
                sec = ds

        val = best_r_val * 2 - sec
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]