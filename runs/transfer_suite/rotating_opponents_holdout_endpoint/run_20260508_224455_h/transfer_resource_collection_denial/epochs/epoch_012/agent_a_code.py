def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    self_on = (sx, sy) in obstacles
    if (sx, sy) in resources:
        return [0, 0]

    if not resources:
        best = (-10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            sc = (md(nx, ny, ox, oy), -(dx == 0 and dy == 0))
            if best[1] is None or sc > best[0]:
                best = (sc, (dx, dy))
        return list(best[1]) if best[1] is not None else [0, 0]

    # Greedy advantage: after the move, pick the resource with best (oppDist - selfDist),
    # favor closer self and better immediate advantage.
    best_move = (None, (-10**18, 10**9, 10**9))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        best_r = None
        best_r_val = (-10**18, 10**9, 10**9)
        for rx, ry in resources:
            d_self = md(nx, ny, rx, ry)
            d_opp = md(ox, oy, rx, ry)
            # advantage first, then self proximity, then deterministic by coordinates
            val = (d_opp - d_self, -d_self, -(rx + 31 * ry))
            if best_r is None or val > best_r_val:
                best_r = (rx, ry)
                best_r_val = val
        # overall tie-break: prefer staying if equal, then lexicographic move determinism
        stay_bias = 1 if (dx == 0 and dy == 0) else 0
        overall = (best_r_val[0], best_r_val[1], stay_bias)
        if best_move[0] is None or overall > best_move[1] or (overall == best_move[1] and (dx, dy) < best_move[0]):
            best_move = ((dx, dy), overall)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]