def choose_move(observation):
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in observation.get('obstacles', []) or [])
    remaining = observation.get('remaining_resource_count', len(resources))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles
    def dist(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If resources exist, target closest resource with opponent-aware heuristic
    target = None
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((sx, sy), (ox, oy))  # not used directly, but keep deterministic
            do_r = dist((ox, oy), (rx, ry))
            key = (do_r - ds, -ds)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        target = best

    # Evaluate viable moves toward target or center if no target
    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            viable.append((dx, dy, nx, ny))
    if not viable:
        return [0, 0]

    def score_move(dx, dy, nx, ny):
        # prefer moves toward target if exists
        s = 0
        if target is not None:
            tx, ty = target
            s -= dist((nx, ny), (tx, ty))
        # avoid stepping into opponent
        if (nx, ny) == (ox, oy):
            s -= 100
        # prefer moves that reduce distance to opponent slightly to anticipate collision avoidance
        s += dist((nx, ny), (ox, oy)) * -0.5
        return s

    best_move = None
    best_s = None
    for dx, dy, nx, ny in viable:
        sc = score_move(dx, dy, nx, ny)
        if best_s is None or sc > best_s:
            best_s = sc
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]