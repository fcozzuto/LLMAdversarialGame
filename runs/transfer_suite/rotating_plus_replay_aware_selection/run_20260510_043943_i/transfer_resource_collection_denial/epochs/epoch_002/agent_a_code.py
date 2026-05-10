def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in observation.get("obstacles", []) or [])

    deltas = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            deltas.append((dx, dy))
    deltas.sort(key=lambda d: (abs(d[0]) + abs(d[1]), -abs(d[0] * d[1]), d[0], d[1]))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    target = None
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            # Prefer resources we can reach sooner; slight tie-break for closer.
            key = (ds - 0.95 * do, ds, -rx, -ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        target = best if best is not None else None
    if target is None:
        target = ((w - 1) // 2, (h - 1) // 2)

    best_move = (0, 0)
    best_score = None
    res_set = set(tuple(p) for p in resources)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        nds = dist((nx, ny), target)
        ndo = dist((ox, oy), target)
        score = (-nds + 0.15 * (ndo - nds))

        if (nx, ny) in res_set:
            score += 1000  # guarantee collection priority

        # If target is reached, prefer staying/finishing rather than drifting.
        if nds == 0:
            score += 10

        key = (-(score),)  # maximize score
        if best_score is None or key < best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]