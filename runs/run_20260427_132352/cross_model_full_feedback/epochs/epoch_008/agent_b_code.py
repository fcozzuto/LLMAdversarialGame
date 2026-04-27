def choose_move(observation):
    turn_index = observation.get('turn_index', 0)
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation.get('self_position', [0, 0])
    ox, oy = observation.get('opponent_position', [0, 0])
    resources = observation.get('resources', []) or []
    obs = set(tuple(p) for p in (observation.get('obstacles', []) or []))
    remaining = observation.get('remaining_resource_count', len(resources))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1), (-1,0), (-1,1),
            (0,-1), (0,0), (0,1),
            (1,-1), (1,0), (1,1)]

    def md(a, b):
        return abs(a[0]-b[0]) + abs(a[1]-b[1])

    # If resources exist, move toward closest resource while avoiding opponent's square area
    target = None
    if resources:
        closest = None
        bestd = None
        for r in resources:
            d = md((sx, sy), tuple(r))
            if bestd is None or d < bestd:
                closest = tuple(r)
                bestd = d
        target = closest

    if target is None:
        target = ((w-1)//2, (h-1)//2)

    # Pick a move that reduces distance to target while staying free
    best = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = md((nx, ny), target)
        # Deterministic tie-breaker: smaller dx, then smaller dy
        key = (d, dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    # If no move found (surrounded), stay
    if best is None:
        return [0, 0]
    return best_move