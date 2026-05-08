def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def free(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cell_key(cx, cy, target):
        tx, ty = target
        ds = dist((cx, cy), (tx, ty))
        do = dist((ox, oy), (tx, ty))
        return (ds - do, ds, tx, ty, cx, cy)

    # Choose target we can reach sooner than the opponent (tie-break by coords).
    if resources:
        best_t, best_key = None, None
        for r in resources:
            if r in obstacles:
                continue
            ds = dist((x, y), r)
            do = dist((ox, oy), r)
            key = (ds - do, ds, r[0], r[1])
            if best_key is None or key < best_key:
                best_key, best_t = key, r
        target = best_t if best_t is not None else (w // 2, h // 2)
    else:
        target = (w // 2, h // 2)

    # Greedy move: among legal adjacent cells, pick the one best for the chosen target.
    best_move, best_val = (0, 0), None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not free(nx, ny):
            continue
        val = cell_key(nx, ny, target)
        if best_val is None or val < best_val:
            best_val, best_move = val, [dx, dy]

    return best_move