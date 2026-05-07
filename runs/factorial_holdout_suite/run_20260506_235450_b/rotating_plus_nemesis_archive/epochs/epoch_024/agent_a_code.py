def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    raw_obs = observation.get("obstacles") or []
    obstacles = set()
    for p in raw_obs:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if (x, y) not in obstacles]
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d_self = min(cheb(nx, ny, rx, ry) for rx, ry in res)
        d_opp = cheb(nx, ny, ox, oy)
        hit = 1 if (nx, ny) in set(res) else 0
        score = (-d_self) + (0.15 * d_opp) + (2.5 * hit)
        if score > best_score or (score == best_score and (best is None or (dx, dy) < best)):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]