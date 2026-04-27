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
        best = None
        best_score = None
        for dx, dy, nx, ny in cand:
            d_to_res = min((dist((nx, ny), r) for r in resources), default=999)
            # Prefer closer to any resource, break ties by staying closer to center-ish
            center_dist = dist((nx, ny), (w//2, h//2))
            score = (d_to_res, center_dist)
            if best is None or score < best_score:
                best = (dx, dy, nx, ny)
                best_score = score
        if best is not None:
            return [best[0], best[1]]

    # No resources reachable or considered; move toward opponent to pressure
    # Choose move that reduces Manhattan distance to opponent if possible
    best_move = None
    best_md = dist((sx, sy), (ox, oy))
    for dx, dy, nx, ny in cand:
        md = dist((nx, ny), (ox, oy))
        if md < best_md:
            best_md = md
            best_move = (dx, dy)
    if best_move:
        return [best_move[0], best_move[1]]

    # If no improvement, stay or cycle minimally
    return [0, 0]