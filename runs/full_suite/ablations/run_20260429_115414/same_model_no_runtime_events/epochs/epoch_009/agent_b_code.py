def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    grid_res = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))
    res = []
    for p in grid_res:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    threat = None
    if res:
        for rx, ry in sorted(res):
            if cheb(ox, oy, rx, ry) <= 1:
                threat = (rx, ry)
                break
    best = (0, 0); bestv = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        v = 0
        if threat is not None:
            trx, try_ = threat
            v += 500 - 50 * cheb(nx, ny, trx, try_)
            v += 80 if cheb(ox, oy, trx, try_) <= cheb(nx, ny, trx, try_) else 0
        else:
            if res:
                near = min(cheb(nx, ny, rx, ry) for rx, ry in res)
                v += 200 if (nx, ny) in res else 0
                v += 60 - 10 * near
        # discourage moving next to opponent too much
        v -= 20 * cheb(nx, ny, ox, oy)
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v; best = (dx, dy)
    return [best[0], best[1]]