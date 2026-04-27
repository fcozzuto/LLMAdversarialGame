def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h:
            resources.append((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if resources:
        # Move toward nearest resource, avoid getting too close to opponent if possible
        best = None
        bestv = 10**9
        for dx, dy, nx, ny in cand:
            d_r = min(dist((nx, ny), r) for r in resources)
            d_o = dist((nx, ny), (ox, oy))
            v = d_r * 2 - d_o  # prioritize nearer resources, deter distance to opponent
            if v < bestv:
                bestv = v
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]
    # If no resources or tie, head toward center while avoiding obstacles and staying deterministic
    tx, ty = w // 2, h // 2
    best = None
    bestv = 10**9
    for dx, dy, nx, ny in cand:
        v = dist((nx, ny), (tx, ty))
        # also reward keeping distance from opponent modestly
        v -= dist((nx, ny), (ox, oy)) * 0.1
        if v < bestv:
            bestv = v
            best = (dx, dy, nx, ny)
    if best is not None:
        return [best[0], best[1]]

    # fallback
    return [0, 0]