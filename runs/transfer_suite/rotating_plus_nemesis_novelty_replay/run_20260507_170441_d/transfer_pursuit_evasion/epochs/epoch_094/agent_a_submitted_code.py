def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w) if w is not None else 8
        h = int(h) if h is not None else 8
    except:
        w, h = 8, 8

    def pos(p):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            return int(p[0]), int(p[1])
        if isinstance(p, dict) and "x" in p and "y" in p:
            return int(p["x"]), int(p["y"])
        return 0, 0

    sx, sy = pos(observation.get("self_position", [0, 0]))
    ox, oy = pos(observation.get("opponent_position", [0, 0]))

    obstacles = set()
    obs = observation.get("obstacles") or []
    for o in obs:
        x, y = None, None
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = o[0], o[1]
        elif isinstance(o, dict) and "x" in o and "y" in o:
            x, y = o["x"], o["y"]
        if x is None or y is None:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources") or []
    res_list = []
    for r in resources:
        x, y = None, None
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        elif isinstance(r, dict) and "x" in r and "y" in r:
            x, y = r["x"], r["y"]
        if x is None or y is None:
            continue
        try:
            x, y = int(x), int(y)
        except:
            continue
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res_list.append((x, y))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return dx if dx >= 0 else -dx if -dx > dy if dy >= 0 else -dy

    # fix cheb deterministically without weird expressions
    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = None
    if res_list:
        best = None
        bestd = None
        for p in res_list:
            d = dist((sx, sy), p)
            if bestd is None or d < bestd or (d == bestd and (p[0], p[1]) < best):
                bestd = d
                best = p
        target = best
    else:
        target = (ox, oy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist((nx, ny), target)
        # Prefer shorter distance; then prefer moving (not staying); then stable tie-break by dx,dy
        score = (d, 0 if (dx == 0 and dy == 0) else -1, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]