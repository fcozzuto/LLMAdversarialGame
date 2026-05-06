def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except Exception:
            pass

    resources = observation.get("resources", []) or []
    if not resources:
        resources = []

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def score_toward(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    target = None
    best = None
    for r in resources:
        try:
            rx, ry = r[0], r[1]
        except Exception:
            continue
        ds = score_toward(sx, sy, rx, ry)
        do = score_toward(ox, oy, rx, ry)
        # Prefer resources we are closer to; tie-break deterministically by position
        v = (do <= ds, ds, rx, ry)
        if best is None or v < best:
            best = v
            target = (rx, ry)

    best_move = [0, 0]
    bestv = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        if target is None:
            v = ((nx - cx) ** 2 + (ny - cy) ** 2, nx, ny)
        else:
            rx, ry = target
            ds = score_toward(nx, ny, rx, ry)
            do = score_toward(nx, ny, ox, oy)
            # Stay close to target while keeping some distance from opponent
            v = (ds, -do, nx, ny)
        if bestv is None or v < bestv:
            bestv = v
            best_move = [dx, dy]

    return best_move