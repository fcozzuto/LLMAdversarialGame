def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    is_pursuer = ("purs" in self_role) or ("purs" not in self_role and "evad" in opp_role)
    if ("evad" in self_role) and ("purs" not in self_role):
        is_pursuer = False
    elif ("purs" in self_role) and ("evad" not in self_role):
        is_pursuer = True

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best = None
    best_key = None

    for dx, dy, nx, ny in moves:
        md = abs(nx - ox) + abs(ny - oy)
        # Prefer moves that reduce both axes when pursuing; for evading, prefer the opposite.
        axis_bias = (abs(nx - ox) - abs(ny - oy))
        turn_pen = 1 if (dx == 0 and dy == 0) else 0
        if is_pursuer:
            score = (-md, -(abs(nx - ox) + abs(ny - oy) - 0), abs(axis_bias), turn_pen)
        else:
            score = (md, -(abs(axis_bias)), -turn_pen, 0)

        if best is None or score > best_key:
            best_key = score
            best = [dx, dy]

    return best