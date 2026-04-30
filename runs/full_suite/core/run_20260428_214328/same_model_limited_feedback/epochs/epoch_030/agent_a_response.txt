def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    best = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach sooner; tie-break deterministically by coordinates.
        key = (ds - do, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best

    def step_ok(dx, dy):
        nx, ny = sx + dx, sy + dy
        return in_bounds(nx, ny) and (nx, ny) not in obstacles

    # Greedy: among valid moves, pick one that minimizes distance to target and wins tie-break.
    cur_best = None
    cur_move = (0, 0)
    for dx, dy in dirs:
        if not step_ok(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        d = dist((nx, ny), (tx, ty))
        # Also prefer moves that don't run away from target too much.
        key = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
        if cur_best is None or key < cur_best:
            cur_best = key
            cur_move = (dx, dy)

    return [int(cur_move[0]), int(cur_move[1])]