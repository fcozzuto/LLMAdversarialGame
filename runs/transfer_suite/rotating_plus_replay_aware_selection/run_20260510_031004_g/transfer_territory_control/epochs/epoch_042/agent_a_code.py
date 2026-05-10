def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    px, py = observation.get("opponent_position", (0, 0))

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    unclaimed = list(map(tuple, observation.get("unclaimed_cells", observation.get("resources", []))))
    if not unclaimed:
        unclaimed = [tuple(p) for p in observation.get("resources", [])]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def best_target():
        best = None
        bestk = None
        for x, y in unclaimed:
            if not inb(x, y):
                continue
            ds = dist((sx, sy), (x, y))
            do = dist((px, py), (x, y))
            k = (0 if ds <= do else 1, ds, do, x, y)
            if bestk is None or k < bestk:
                bestk = k
                best = (x, y)
        return best

    target = best_target()
    if target is None:
        tx, ty = px, py
    else:
        tx, ty = target

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((dx, dy, nx, ny))

    # Greedy: move that most reduces distance to target; tie-break with opponent distance and determinism.
    best = None
    bestk = None
    for dx, dy, nx, ny in candidates:
        ds = dist((nx, ny), (tx, ty))
        do = dist((nx, ny), (px, py))
        k = (ds, do, dx, dy)
        if bestk is None or k < bestk:
            bestk = k
            best = (dx, dy)
    return [int(best[0]), int(best[1])]