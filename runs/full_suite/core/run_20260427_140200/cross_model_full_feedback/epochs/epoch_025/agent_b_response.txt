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
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    free = lambda x, y: inb(x, y) and (x, y) not in obstacles

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

    # Prefer moving toward a resource if beneficial
    if resources:
        best = None
        best_score = -10
        for dx, dy, nx, ny in cand:
            # distance to nearest resource from new pos
            ndist = min(dist((nx, ny), r) for r in resources)
            # distance to opponent from new pos (avoid giving easy chase)
            odist = dist((nx, ny), (ox, oy))
            score = -ndist + (odist * 0.2)
            if score > best_score:
                best_score = score
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]

    # If no resources or tie, move to maximize distance from opponent while staying close to center
    centerx, centery = w/2, h/2
    best = None
    best_score = -9999
    for dx, dy, nx, ny in cand:
        dopp = dist((nx, ny), (ox, oy))
        dist_center = dist((nx, ny), (centerx, centery))
        score = -dopp + dist_center * 0.5
        if score > best_score:
            best_score = score
            best = (dx, dy, nx, ny)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]