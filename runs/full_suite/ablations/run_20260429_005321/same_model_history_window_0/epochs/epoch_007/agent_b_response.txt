def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource by (our distance, -opponent distance) to be contested less.
    best = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        score = (d1, -d2, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    if best is None:
        # No known resources: move toward opponent to deny space deterministically
        tx, ty = ox, oy
    else:
        _, (tx, ty) = best

    # If already on a resource, try to hold position (collection should happen automatically).
    if (sx, sy) in resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cur = (sx, sy)

    def safe_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            return None
        if (nx, ny) in obstacles:
            return None
        return (nx, ny)

    best_next = None
    best_val = None
    for dx, dy in candidates:
        nxt = safe_move(dx, dy)
        if nxt is None:
            continue
        nx, ny = nxt
        # Greedy objective: closer to target, but also avoid stepping into positions adjacent to obstacles when possible.
        d_t = dist(nxt, (tx, ty))
        d_o = dist(nxt, (ox, oy))
        # Small penalty for being near obstacles to reduce getting stuck.
        near_obs = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ax, ay = nx + adx, ny + ady
                if inb(ax, ay) and (ax, ay) in obstacles:
                    near_obs += 1
        val = (d_t, -d_o, near_obs, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_next = (dx, dy)

    if best_next is None:
        return [0, 0]
    return [int(best_next[0]), int(best_next[1])]