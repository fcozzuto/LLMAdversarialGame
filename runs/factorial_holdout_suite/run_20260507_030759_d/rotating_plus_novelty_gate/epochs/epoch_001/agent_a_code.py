def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        return abs(ax - bx) + abs(ay - by)

    # Choose resource where we are relatively closest vs opponent
    best = None
    best_key = None
    for rx, ry in resources:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    moves.sort()

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        nds = dist((nx, ny), (tx, ty))
        ndo = dist((ox, oy), (tx, ty))
        # Prefer reducing our distance; if tied, prefer resources that are farther from opponent after their next step? (approx: keep do)
        mkey = (nds, ndo, abs(nx - w // 2) + abs(ny - h // 2), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]