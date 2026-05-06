def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    resources = observation.get("resources", []) or []
    if not resources:
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        return [dx, dy]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            obstacles.add((p[0], p[1]))
        except:
            pass

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_cmp = None
    for r in resources:
        rx, ry = r[0], r[1]
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds > do, ds, -do, rx, ry)
        if best is None or key < best_cmp:
            best, best_cmp = (rx, ry), key

    tx, ty = best
    best_move = None
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = dist((nx, ny), (tx, ty))
        if best_d is None or nd < best_d or (nd == best_d and (dx, dy) < best_move):
            best_d = nd
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]