def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_dx, best_dy = 0, 0
    if res:
        best_r = None
        best_score = -10**9
        for r in res:
            rx, ry = r[0], r[1]
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            score = ds - do
            if score > best_score or (score == best_score and (rx, ry) < (best_r[0], best_r[1])):
                best_score = score
                best_r = (rx, ry)

        rx, ry = best_r
        best_val = 10**9
        best_tie = (10**9, 10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, rx, ry)
            # tie-break: prefer smaller opponent distance, then lexicographically by move
            oppd = cheb(nx, ny, ox, oy)
            val = (d, oppd)
            if val < (best_val, best_tie[1]) or (val[0] == best_val and val[1] < best_tie[1]):
                best_val = val[0]
                best_tie = val
                best_dx, best_dy = dx, dy
        return [best_dx, best_dy]

    # No resources: drift toward the opposite corner from opponent
    tx = gw - 1 if ox < gw // 2 else 0
    ty = gh - 1 if oy < gh // 2 else 0
    best_val = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        if d < best_val or (d == best_val and (dx, dy) < (best_dx, best_dy)):
            best_val = d
            best_dx, best_dy = dx, dy
    return [best_dx, best_dy]