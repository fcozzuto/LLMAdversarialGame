def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        tx = 0 if cx == sx else (1 if cx > sx else -1)
        ty = 0 if cy == sy else (1 if cy > sy else -1)
        for dx, dy in [(tx, 0), (0, ty), (tx, ty), (0, 0)]:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) != (ox, oy):
                return [dx, dy]
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_r = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) == 2):
            continue
        rx, ry = r[0], r[1]
        if (rx, ry) == (sx, sy):
            continue
        if not inside(rx, ry):
            continue
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        key = (-(od - sd), sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    rx, ry = best_r
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    target_steps = [(tx, 0), (0, ty), (tx, ty), (0, 0), (-tx, 0), (0, -ty)]
    tried = set()
    for dx, dy in target_steps:
        if (dx, dy) in tried:
            continue
        tried.add((dx, dy))
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) != (ox, oy):
            return [dx, dy]

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) == (ox, oy):
            continue
        score = (dist(nx, ny, rx, ry), dist(nx, ny, ox, oy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move