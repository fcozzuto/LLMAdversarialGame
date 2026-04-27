def choose_move(observation):
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obstacles = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    remaining = observation.get('remaining_resource_count', len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    dirs = [(-1,-1), (-1,0), (-1,1),
            (0,-1), (0,0), (0,1),
            (1,-1), (1,0), (1,1)]

    # choose target: closest resource if any, else center
    if resources:
        target = min((tuple(r) for r in resources), key=lambda p: dist((sx, sy), p))
    else:
        target = ((w - 1) // 2, (h - 1) // 2)

    best_score = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        d_to_t = dist((nx, ny), target)
        d_to_o = dist((nx, ny), (ox, oy))

        # Heuristic: move toward target, stay away from opponent
        score = (-2 * d_to_t) - (2 * d_to_o)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    # Fallback: if no move found (all blocked), stay
    if best_score is None:
        return [0, 0]
    return best_move