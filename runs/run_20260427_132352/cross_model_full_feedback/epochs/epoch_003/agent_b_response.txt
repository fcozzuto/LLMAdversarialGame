def choose_move(observation):
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    remaining = observation.get('remaining_resource_count', len(resources))

    # Possible moves (dx, dy)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles or (x == ox and y == oy)

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # evaluate viable moves (not stepping into obstacle or opponent)
    viable = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and not blocked(nx, ny):
            viable.append((dx, dy, nx, ny))

    if not viable:
        return [0, 0]

    # Target closest resource if any
    target = None
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            key = (do - ds, -ds)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        target = best

    if target:
        tx, ty = target
        # Choose move that gets closer to target while staying in viable
        best_move = None
        best_dist = None
        for dx, dy, nx, ny in viable:
            d = dist((nx, ny), (tx, ty))
            if best_dist is None or d < best_dist:
                best_dist = d
                best_move = (dx, dy, nx, ny)
        if best_move:
            return [best_move[0], best_move[1]]

    # If no target or cannot reach, move to maximize distance from opponent while staying viable
    best_move = None
    best_metric = None
    for dx, dy, nx, ny in viable:
        d_op = dist((nx, ny), (ox, oy))
        # Prefer moving away from opponent, with a bias to diagonals
        away = (nx - ox, ny - oy)
        bias = 0
        if away != (0,0):
            bias = (1 if away[0] > 0 else -1) + (1 if away[1] > 0 else -1)
        metric = d_op * 2 + bias
        if best_metric is None or metric > best_metric:
            best_metric = metric
            best_move = (dx, dy)
    if best_move:
        return [best_move[0], best_move[1]]

    # Fallback
    return [0, 0]