def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        # Head to the farthest corner from opponent deterministically
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestv = (-1, -1)
        for cx, cy in corners:
            v = (abs(cx - ox) + abs(cy - oy), -(abs(cx - sx) + abs(cy - sy)))
            if v > bestv:
                bestv = v
                best = (cx, cy)
        tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set and (sx, sy) not in obstacles:
        return [0, 0]

    # Pick resource where we are ahead by distance; then break ties by closer distance
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        lead = do - ds
        key = (lead, -ds, - (abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    # Evaluate legal moves locally toward chosen target
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    opp_best_d = man(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        ds = man(nx, ny, tx, ty)
        # Prefer reducing our distance, and maintaining/creating advantage over opponent
        score = (opp_best_d - ds, -ds, -(abs(nx - ox) + abs(ny - oy)), 1 if (nx, ny) in res_set else 0)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]