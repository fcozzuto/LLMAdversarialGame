def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
    if not res:
        return [0, 0]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_t = None
    best_score = None
    for rx, ry in res:
        sd = dist((sx, sy), (rx, ry))
        od = dist((ox, oy), (rx, ry))
        score = (od - sd) * 3 - sd  # prefer resources closer than opponent; otherwise closer to us
        if best_score is None or score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    best_move = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Greedy toward target with slight anti-opponent pressure
        myd = dist((nx, ny), (tx, ty))
        opd = dist((ox, oy), (tx, ty))
        val = (opd - myd) * 3 - myd
        # small preference to reduce Manhattan to target
        val -= (0 if (nx, ny) == (tx, ty) else 0)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If somehow all neighbors invalid, stay
    return [int(best_move[0]), int(best_move[1])]