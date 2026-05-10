def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            rx, ry = int(p[0]), int(p[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def distmax(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_score = None
    for (rx, ry) in res:
        sd = distmax((sx, sy), (rx, ry))
        od = distmax((ox, oy), (rx, ry))
        score = (od - sd, -sd, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)
    tx, ty = best

    dx = tx - sx
    dy = ty - sy
    if dx > 1: dx = 1
    if dx < -1: dx = -1
    if dy > 1: dy = 1
    if dy < -1: dy = -1

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue
        candidates.append((mx, my))

    if not candidates:
        return [0, 0]

    def cand_key(mx, my):
        nx, ny = sx + mx, sy + my
        nsd = distmax((nx, ny), (tx, ty))
        nod = distmax((ox, oy), (tx, ty))
        return (nod - nsd, -nsd, -nx, -ny)

    best_m = None
    best_k = None
    for mx, my in candidates:
        k = cand_key(mx, my)
        if best_k is None or k > best_k:
            best_k = k
            best_m = (mx, my)

    return [int(best_m[0]), int(best_m[1])]