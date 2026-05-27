def choose_move(observation):
    def p(v):
        if isinstance(v, (list, tuple)) and len(v) >= 2:
            return int(v[0]), int(v[1])
        if isinstance(v, dict):
            x = v.get("x", v.get("col"))
            y = v.get("y", v.get("row"))
            if x is not None and y is not None:
                return int(x), int(y)
        return None

    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    s = p(observation.get("self_position")) or (0, 0)
    o = p(observation.get("opponent_position")) or (0, 0)
    sx, sy = s
    ox, oy = o

    def gather(v):
        r = []
        if isinstance(v, dict):
            for k in ("positions", "cells", "tiles", "items", "points", "nodes", "coords", "resources", "obstacles"):
                if k in v:
                    r += gather(v[k])
        elif isinstance(v, (list, tuple)):
            for a in v:
                q = p(a)
                if q is not None:
                    r.append(q)
        return r

    res = gather(observation.get("resources"))
    obs = set(gather(observation.get("obstacles")))
    if (sx, sy) in obs:
        obs.remove((sx, sy))

    best = (0, 0)
    best_score = -10**9
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= W or ny >= H or (nx, ny) in obs:
            continue
        if res:
            dr = min(abs(nx - rx) + abs(ny - ry) for rx, ry in res)
        else:
            dr = abs(nx - ox) + abs(ny - oy)
        do = abs(nx - ox) + abs(ny - oy)
        score = -dr * 5 + do
        if dx == 0 and dy == 0:
            score -= 1
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [int(best[0]), int(best[1])]
