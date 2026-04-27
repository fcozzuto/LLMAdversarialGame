def choose_move(observation):
    # Minimal deterministic strategy: move greedily toward closest resource while avoiding opponent and obstacles.
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

    # 9 possible moves (including stay)
    dirs = [(-1,-1), (-1,0), (-1,1),
            (0,-1), (0,0), (0,1),
            (1,-1), (1,0), (1,1)]

    def dist(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # target: closest resource
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

    # If no resources, head toward center
    if target is None:
        target = ((w-1)//2, (h-1)//2)

    # Choose a move that minimizes distance to target, break ties deterministically
    best_move = (0, 0)
    best_d = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = dist((nx, ny), target)
        # prefer not stepping onto opponent if possible
        if nx == ox and ny == oy:
            continue
        if best_d is None or d < best_d or (d == best_d and (dx, dy) < best_move):
            best_d = d
            best_move = (dx, dy)

    # If no legal move found (surrounded or blocked), stay
    if best_move is None:
        best_move = (0, 0)

    return [best_move[0], best_move[1]]