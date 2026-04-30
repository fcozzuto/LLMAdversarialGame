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
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
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
        # go toward nearest resource
        best = None
        bestd = 10**9
        for dx, dy, nx, ny in cand:
            d = min(dist((nx, ny), r) for r in resources)
            if d < bestd:
                bestd = d
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]

    # no resources or no reachable resource: prefer move that increases distance from opponent while staying within bounds and free
    best = None
    bestscore = -10**9
    for dx, dy, nx, ny in cand:
        od = dist((nx, ny), (ox, oy))
        # score: prefer farther from opponent, with some bias to stay central
        centerx, centery = w // 2, h // 2
        centerd = dist((nx, ny), (centerx, centery))
        score = -od + centerd * 0.1
        if score > bestscore:
            bestscore = score
            best = (dx, dy, nx, ny)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]