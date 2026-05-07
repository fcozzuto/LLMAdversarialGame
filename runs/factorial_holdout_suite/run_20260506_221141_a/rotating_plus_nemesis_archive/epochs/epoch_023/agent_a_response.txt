def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources or not valid(sx, sy):
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if valid(r[0], r[1]) or (r[0], r[1]) == (sx, sy)]
    if not res:
        return [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score(x, y):
        best = None
        for rx, ry in res:
            sd = dist(x, y, rx, ry)
            od = dist(ox, oy, rx, ry)
            margin = od - sd  # positive if we are closer
            cand = (margin, -sd, -rx, -ry)
            if best is None or cand > best:
                best = cand
        return best

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = (0, 0)
    best_sc = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sc = cell_score(nx, ny)
        if best_sc is None or sc > best_sc:
            best_sc = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]