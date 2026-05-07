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

    def manh(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int)):
            continue
        if not (0 <= tx < w and 0 <= ty < h):
            continue
        if (tx, ty) in obs:
            continue
        myd = manh(sx, sy, tx, ty)
        opd = manh(ox, oy, tx, ty)
        key = (opd - myd, -myd, tx + ty * 0.0001)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [
        (dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)
    ]
    best_move = (0, 0)
    best_dist = None

    for cx, cy in candidates:
        nx, ny = sx + cx, sy + cy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        d = manh(nx, ny, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (cx, cy) > best_move):
            best_dist = d
            best_move = (cx, cy)

    return [int(best_move[0]), int(best_move[1])]