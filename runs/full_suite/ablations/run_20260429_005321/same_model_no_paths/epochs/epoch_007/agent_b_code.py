def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    move_list = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in move_list:
        move_list.append((0, 0))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inside(x, y) and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obstacle_prox(x, y):
        pen = 0
        for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                pen += 1
        return pen

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in move_list:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (man(nx, ny, tx, ty), obstacle_prox(nx, ny))
            if best is None or key < best[0]:
                best = (key, dx, dy)
        if best is None:
            return [0, 0]
        return [best[1], best[2]]

    best_score = None
    best_move = (0, 0)
    for dx, dy in move_list:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Primary: maximize advantage to some resource (opponent closer -> bad).
        best_adv = -10**9
        best_ourd = 10**9
        for rx, ry in resources:
            ourd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - ourd
            if adv > best_adv or (adv == best_adv and ourd < best_ourd):
                best_adv, best_ourd = adv, ourd
        # Secondary: reduce opponent's immediate threat by also considering our distance after next step? (approx)
        # Tertiary: obstacle proximity penalty
        score = (best_adv, -best_ourd, -(obstacle_prox(nx, ny)))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]