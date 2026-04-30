def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def step_toward(tx, ty):
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d = dist((nx, ny), (tx, ty))
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)
        if best is None:
            best = (0, 0)
        return [best[0], best[1]]

    if resources:
        best_res = None
        best_metric = 10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obstacles:
                continue
            metric = dist((sx, sy), (rx, ry)) - dist((ox, oy), (rx, ry))
            if metric < best_metric or (metric == best_metric and (rx, ry) < tuple(best_res or r)):
                best_metric = metric
                best_res = (rx, ry)
        return step_toward(best_res[0], best_res[1])

    # No resources: move to maximize advantage by increasing distance from opponent
    best = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        val = dist((nx, ny), (ox, oy))
        if val > best_val:
            best_val = val
            best = (dx, dy)
    return [best[0], best[1]]