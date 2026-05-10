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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_score = None
    for rx, ry in res:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        score = (od - sd, -sd, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best = (rx, ry)
    tx, ty = best

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        # Higher is better: stay closer to target and discourage opponent proximity
        sdn = dist((nx, ny), (tx, ty))
        odn = dist((ox, oy), (tx, ty))
        candidates.append(((odn - sdn, -sdn, -nx, -ny), [dx, dy]))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]