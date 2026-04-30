def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obs

    if not res:
        best = (0, 0)
        bestd = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d > bestd or (d == bestd and (nx + ny) > (best[0] + best[1])):
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        near_self = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < near_self:
                near_self = d
        if (nx, ny) in res:
            near_self = -1  # guarantee pickup preference

        near_opp = 10**9
        for rx, ry in res:
            d = cheb(ox, oy, rx, ry)
            if d < near_opp:
                near_opp = d
        # If we're closer to some resource than opponent, push; else keep distance
        opp_dist = cheb(nx, ny, ox, oy)
        score = (100 if near_self < 0 else 0) - near_self * 2 + (opp_dist * 0.1)
        if near_self >= 0 and near_opp <= near_self:
            score -= 8  # avoid dead zones where opponent likely contests

        tie = (nx + ny)  # deterministic tie-break
        if score > best_score or (score == best_score and tie > (sx + sy)):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]