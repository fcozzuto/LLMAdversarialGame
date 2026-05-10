def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except:
            pass

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = observation.get("resources", []) or []
    targets = []
    for r in res:
        try:
            x, y = r
            targets.append((int(x), int(y)))
        except:
            pass

    if targets:
        tx, ty = min(targets, key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    else:
        tx, ty = ox, oy

    best = None
    bestv = None
    for dx, dy in moves:
        nx, ny = int(sx) + dx, int(sy) + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    adj_obs += 1
        near_opp = md(nx, ny, ox, oy)
        v = (-d) + (-0.2 * adj_obs) + (0.05 * near_opp)
        key = (v, -dx, -dy, nx, ny)
        if bestv is None or key > bestv:
            bestv = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best