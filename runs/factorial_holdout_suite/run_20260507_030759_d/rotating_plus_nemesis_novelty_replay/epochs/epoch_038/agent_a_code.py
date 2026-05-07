def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def sq(a, b):
        return a * a + b * b

    def nearest_res_dist2(x, y):
        if not res:
            return None
        best = None
        for rx, ry in res:
            d = sq(rx - x, ry - y)
            if best is None or d < best:
                best = d
        return best

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dr2 = nearest_res_dist2(nx, ny)
        do2 = sq(ox - nx, oy - ny)

        if dr2 is None:
            score = do2 * 1.0
        else:
            score = -dr2 * 10.0 + do2 * 0.2

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]