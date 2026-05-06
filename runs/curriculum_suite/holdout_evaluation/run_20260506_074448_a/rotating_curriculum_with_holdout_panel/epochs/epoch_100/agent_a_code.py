def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            sc = (manhattan(nx, ny, tx, ty), manhattan(nx, ny, ox, oy))
            key = (sc[0], -sc[1], dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    # Pick the resource most threatening to the opponent (smallest opp distance).
    target = None
    best_opp = None
    for rx, ry in resources:
        d = manhattan(ox, oy, rx, ry)
        if best_opp is None or d < best_opp or (d == best_opp and (rx, ry) < target):
            best_opp = d
            target = (rx, ry)
    rx, ry = target

    best_key = None
    best_move = (0, 0)
    oppd = manhattan(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = manhattan(nx, ny, rx, ry)
        # Prefer moves that make us reach the target no later than the opponent,
        # otherwise try to reduce their advantage (deny).
        reach_flag = 0 if ns <= oppd else 1
        denial = oppd - ns  # positive means we're closer than opponent
        # Obstacle/edge bias: slightly prefer increasing distance to opponent when not reaching yet.
        sep_bias = manhattan(nx, ny, ox, oy)
        key = (reach_flag, ns, -denial, -sep_bias, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]