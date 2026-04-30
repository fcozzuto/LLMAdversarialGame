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

    # If resources exist, move toward closest resource while not moving into opponent's immediate capture line
    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        d = dist((nx, ny), (cx, cy)) if False else dist((nx, ny), ((nx, ny)))
        # compute distance to nearest resource
        rdist = min((abs(nx - rx) + abs(ny - ry)) for (rx, ry) in resources) if resources else 0
        # prefer closer to resource, but avoid moving toward opponent if possible
        opp_dist = dist((nx, ny), (ox, oy))
        score = (rdist, -opp_dist)
        if best is None or score < best_score:
            best = (dx, dy, nx, ny)
            best_score = score

    if best is None:
        return [0, 0]
    dx, dy, _, _ = best
    return [dx, dy]