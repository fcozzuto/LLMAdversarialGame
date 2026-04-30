def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    resources = observation.get("resources") or []
    obs = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        d = x1 - x2
        e = y1 - y2
        if d < 0:
            d = -d
        if e < 0:
            e = -e
        return d + e

    def best_valid_neighbors():
        best = []
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if in_bounds(nx, ny) and (nx, ny) not in obstacles:
                best.append((dx, dy, nx, ny))
        return best

    nbrs = best_valid_neighbors()
    if not nbrs:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy, nx, ny in nbrs:
            v = dist(nx, ny, ox, oy) - 0.01 * dist(nx, ny, cx, cy)
            if bestv is None or v > bestv:
                bestv, best = v, (dx, dy)
        return list(best)

    resources_t = [tuple(r) for r in resources]
    resources_t.sort()

    best = None
    bestv = None
    for dx, dy, nx, ny in nbrs:
        v = 0.0
        dself = min(dist(nx, ny, rx, ry) for rx, ry in resources_t)
        dov = min(dist(ox, oy, rx, ry) for rx, ry in resources_t)
        v = dself - 0.6 * dov

        # Small deterministic tie-break: prefer moves that get closer to the closest resource.
        r0 = resources_t[0]
        v += 0.001 * dist(nx, ny, r0[0], r0[1])

        # Prevent drifting into likely opponent adjacency.
        v += 0.05 * dist(nx, ny, ox, oy)
        if bestv is None or v < bestv:
            bestv, best = v, (dx, dy)

    return list(best if best is not None else (0, 0))