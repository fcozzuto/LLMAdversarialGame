def choose_move(observation):
    # Deterministic micro-strategy focusing on approaching nearest resource while avoiding opponent and walls
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in observation.get('obstacles', []) or [])
    remaining = observation.get('remaining_resource_count', len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    # directions including staying
    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1),  (0, 0),  (0, 1),
            (1, -1),  (1, 0),  (1, 1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # choose a target resource deterministically: closest by Manhattan distance
    target = None
    if resources:
        best = None
        best_d = None
        for rx, ry in resources:
            d = dist((sx, sy), (rx, ry))
            if best is None or d < best_d:
                best = (rx, ry)
                best_d = d
        target = best

    # compute a preferred move toward target if possible, otherwise toward center
    if target is not None:
        tx, ty = target
        best_move = (0, 0)
        best_score = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # score: prefer closer to target, deterring staying if not needed, and avoid getting too close to opponent
            d_to_t = dist((nx, ny), (tx, ty))
            d_to_o = dist((nx, ny), (ox, oy))
            score = (-d_to_t, d_to_o)  # closer to target first, then farther from opponent
            if best_score is None or score < best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: move toward center while keeping distance from opponent
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d_to_c = dist((nx, ny), (cx, cy))
        d_to_o = dist((nx, ny), (ox, oy))
        score = (d_to_o, -d_to_c)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]