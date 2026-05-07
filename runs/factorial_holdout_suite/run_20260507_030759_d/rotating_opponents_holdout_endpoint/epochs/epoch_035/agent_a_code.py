def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    deltas.sort()

    def cell_cost(x, y):
        best = None
        for tx, ty in res:
            sd = man(x, y, tx, ty)
            od = man(ox, oy, tx, ty)
            # Prefer contested resources (self not farther than opponent); else penalize.
            contested_pen = 0 if sd <= od else 5
            c = sd + contested_pen * 1 + (-0.1 * od)
            if best is None or c < best:
                best = c
        return best

    best_d = (0, 0)
    best_s = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        s = cell_cost(nx, ny)
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < best_d):
            best_s = s
            best_d = (dx, dy)
    return [int(best_d[0]), int(best_d[1])]