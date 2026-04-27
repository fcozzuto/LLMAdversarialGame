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

    # If there is at least one resource, try to move toward the closest resource,
    # but avoid helping opponent too much: prefer positions not adjacent to opponent.
    target_r = None
    if resources:
        best = None
        best_dxdy = (0, 0)
        for rx, ry in resources:
            d = dist((sx, sy), (rx, ry))
            if best is None or d < best:
                best = d
                target_r = (rx, ry)
        if target_r is not None:
            best_move = None
            best_score = None
            for dx, dy, nx, ny in cand:
                # distance to target
                d_to_r = dist((nx, ny), target_r)
                # discourage moving adjacent to opponent
                adj_to_opp = dist((nx, ny), (ox, oy)) <= 1
                score = -d_to_r - (1 if adj_to_opp else 0)
                if best_score is None or score > best_score:
                    best_score = score
                    best_move = (dx, dy, nx, ny)
            if best_move:
                return [best_move[0], best_move[1]]

    # Fallback: move to maximize distance from opponent while staying legal
    best = None
    best_move = None
    for dx, dy, nx, ny in cand:
        d = dist((nx, ny), (ox, oy))
        if best is None or d > best:
            best = d
            best_move = (dx, dy, nx, ny)
    if best_move:
        return [best_move[0], best_move[1]]

    return [0, 0]