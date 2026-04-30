def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    if resources:
        best_t = resources[0]; best_rel = -10**9
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            rel = opd - myd
            if rel > best_rel:
                best_rel = rel; best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cand = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        score = (opd - myd) * 100  # improve relative capture chance
        score -= cheb(nx, ny, ox, oy) * 5  # avoid getting blocked
        # obstacle adjacency penalty to reduce cornering
        adj = 0
        for ddx, ddy in deltas:
            px, py = nx + ddx, ny + ddy
            if inside(px, py) and (px, py) in obstacles:
                adj += 1
        score -= adj * 2
        # prefer moves that bring us closer to some resource if any
        if resources:
            minres = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            score -= minres
        cand.append((score, nx, ny))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    _, nx, ny = cand[0]
    return [nx - sx, ny - sy]