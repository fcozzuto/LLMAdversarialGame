def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r is None or len(r) < 2:
            continue
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            resources.append((x, y))

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if resources:
        best_move = None
        best_score = None
        for dx, dy, nx, ny in cand:
            # prefer moving toward closest resource, avoid opponent
            d_to_res = min(dist((nx, ny), r) for r in resources)
            d_to_opp = dist((nx, ny), (ox, oy))
            score = -d_to_res * 2 + (-d_to_opp)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy, nx, ny)
        if best_move is not None:
            dx, dy, _, _ = best_move
            return [dx, dy]

    # Else no resources; chase opponent moderately while staying safe
    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        d_to_opp = dist((nx, ny), (ox, oy))
        proximity = -d_to_opp
        # avoid stepping into direct line of sight if possible
        block = (nx, ny) in obstacles
        score = proximity - (1 if block else 0)
        if best_score is None or score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)
    if best is not None:
        dx, dy, _, _ = best
        return [dx, dy]

    return [0, 0]