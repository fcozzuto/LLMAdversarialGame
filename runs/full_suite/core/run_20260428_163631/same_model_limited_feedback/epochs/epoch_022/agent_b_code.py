def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a target resource where we're not heavily out-raced
    best = None
    best_score = None
    for r in resources:
        if r is None:
            continue
        rx, ry = r
        # prefer reachable squares with distance, penalize if opponent is closer
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        score = ds - 2 * do
        # also discourage targets already on top of opponent
        score += 2 * (rx == ox and ry == oy)
        if best is None or (score, ds, rx, ry) < (best_score, best[0], best[1], best[2]):
            best_score = score
            best = (ds, rx, ry)
    if best is None:
        # fallback: drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: smaller distance, then lexicographic dx,dy
    best_move = (0, 0)
    best_metric = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Avoid stepping onto opponent if possible
        avoid_pen = 3 if (nx == ox and ny == oy) else 0
        metric = (dist((nx, ny), (tx, ty)) + avoid_pen, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best_metric is None or metric < best_metric:
            best_metric = metric
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]