def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource we are likely to reach sooner than the opponent.
    target = None
    best = None
    for r in resources:
        rr = (r[0], r[1])
        ds = dist((sx, sy), rr)
        do = dist((ox, oy), rr)
        # Prefer: smaller (ds - do), then closer by ds, then deterministic by coords
        key = (ds - 0.95 * do, ds, rr[0], rr[1])
        if best is None or key < best:
            best = key
            target = rr

    if target is None:
        # No resources: head to center while keeping away from opponent.
        target = (w // 2, h // 2)

    opp = (ox, oy)

    # Choose move maximizing progress to target and separation from opponent, avoiding obstacles.
    best_move = (0, 0)
    best_val = None
    tx, ty = target

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        no = dist((nx, ny), opp)
        # Deterministic tie-break uses move order via (value, nx, ny, dx, dy)
        val = (-ns) + 0.18 * no
        cand = (val, nx, ny, dx, dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    # If all moves were blocked, stay (engine will keep position if invalid).
    dx, dy = best_move
    if isinstance(dx, float) or isinstance(dy, float):
        dx, dy = int(dx), int(dy)
    if dx not in (-1, 0, 1) or dy not in (-1, 0, 1):
        return [0, 0]
    return [dx, dy]