def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid_step(dx, dy):
        nx, ny = sx + dx, sy + dy
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            if valid_step(dx, dy):
                moves.append((dx, dy))
    moves.append((0, 0))

    # Estimate opponent's nearest resource; if they are ahead there, prioritize denying/intercepting it.
    opp_target = min(res, key=lambda p: cheb(ox, oy, p[0], p[1]))
    ds_opp = cheb(sx, sy, opp_target[0], opp_target[1])
    do_opp = cheb(ox, oy, opp_target[0], opp_target[1])

    if do_opp <= ds_opp:
        tx, ty = opp_target
    else:
        # Otherwise, choose best resource by (opponent distance - our distance); break ties by being closer.
        best = max(res, key=lambda p: (cheb(ox, oy, p[0], p[1]) - cheb(sx, sy, p[0], p[1]), -cheb(sx, sy, p[0], p[1])))
        tx, ty = best

    cur = cheb(sx, sy, tx, ty)
    # Deterministically prefer steps that reduce our distance to the chosen target.
    best_move = (0, 0)
    best_key = (-10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        # Secondary: keep away from obstacles by discouraging steps that don't improve.
        improve = cur - d
        # Tertiary: deterministic ordering via lexicographic dx,dy preference.
        key = (improve, -d, -abs(dx) - abs(dy))
        if key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]