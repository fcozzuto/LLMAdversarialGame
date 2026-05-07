def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is None:
            continue
        x, y = p
        obs.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res:
        best = None
        best_score = -10**18
        for rx, ry in res:
            d_me = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            score = (d_opp - d_me) * 1000 - d_me
            if best is None or score > best_score or (score == best_score and (rx, ry) < best):
                best = (rx, ry)
                best_score = score
        tx, ty = best
    else:
        tx, ty = (gw - 1) // 2, (gh - 1) // 2

    best_mv = [0, 0]
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = -cheb(nx, ny, tx, ty)
        if v > best_v or (v == best_v and (dx, dy) < tuple(best_mv)):
            best_v = v
            best_mv = [dx, dy]
    return best_mv