def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    res_list = []
    for r in resources:
        if len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obstacles:
                res_list.append((x, y))
    if not res_list:
        return [0, 0]

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        # Choose the move that maximizes (opponent's closeness advantage over me being minimized)
        # Using manhattan for my approach and Chebyshev for opponent reach to be behaviorally different.
        local_best = None
        local_key = None
        for tx, ty in res_list:
            myd = manh(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # Prefer resources I can reach fast while not letting opponent be too far behind (denial).
            key = (-(myd - opd), -myd, -tx, -ty)
            if local_key is None or key > local_key:
                local_key = key
                local_best = (tx, ty)
        if local_key is None:
            continue
        if best_key is None or local_key > best_key:
            best_key = local_key
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]