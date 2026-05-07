def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def clutter(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    c += 1
        return c

    if not resources:
        return [0, 0]

    res = []
    for r in resources:
        if len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]

    # Estimate opponent's likely target: closest resource to opponent.
    opp_best = min(res, key=lambda t: (md(ox, oy, t[0], t[1]), t[0], t[1]))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best_move = (0, 0, -10**9, 0, 0)
    for dx, dy, nx, ny in moves:
        # Choose best target under a "deny-first" bias against opponent's closest resource.
        best_key = None
        best_val = -10**9
        for tx, ty in res:
            my_d = md(nx, ny, tx, ty)
            opp_d = md(ox, oy, tx, ty)
            if (tx, ty) == opp_best:
                bias = 2.5  # try to contest opponent's likely target
            else:
                bias = 0.0
            val = (opp_d - my_d) * 2.2 + bias - my_d * 0.25 - clutter(tx, ty) * 0.15
            key = (val, -my_d, -clutter(tx, ty), -(tx + ty), -tx, -ty)
            if best_key is None or key > best_key:
                best_key, best_val = key, val

        # Small preference for moving toward main goal direction; tie-break deterministically.
        # Use best_val primarily; then prefer closer to opp_best after move.
        opp_best_d = md(nx, ny, opp_best[0], opp_best[1])
        move_key = (best_val, -opp_best_d, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if move_key > (best_move[2], best_move[3], best_move[4], best_move[0], best_move[1]):
            best_move = (dx, dy, move_key[0], move_key[1], move_key[2])

    return [int(best_move[0]), int(best_move[1])]