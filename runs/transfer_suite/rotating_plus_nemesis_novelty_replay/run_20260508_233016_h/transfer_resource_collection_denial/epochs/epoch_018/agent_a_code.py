def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    alpha = 1.15
    row_bonus_w = 1.2
    col_bonus_w = 0.6
    best_i = 0
    best_cost = None
    for i, (rx, ry) in enumerate(resources):
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        row_bonus = row_bonus_w if ry == oy else 0.0
        col_bonus = col_bonus_w if rx == ox else 0.0
        cost = sd - alpha * od - row_bonus - col_bonus
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_i = i

    tx, ty = resources[best_i]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = None

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not in_bounds(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        oppd = man(ox, oy, tx, ty)
        row_bonus = row_bonus_w if ty == oy else 0.0
        col_bonus = col_bonus_w if tx == ox else 0.0
        # Prefer lowering distance-to-target; also punish giving opponent a closer race
        score = myd - alpha * oppd - row_bonus - col_bonus
        # Small tie-breaker: prefer moves that reduce distance to the opponent (helps denial)
        score2 = score + 0.02 * man(nx, ny, ox, oy)
        if best_score is None or score2 < best_score:
            best_score = score2
            best_move = [mx, my]

    return best_move