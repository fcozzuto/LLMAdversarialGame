def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    if (sx, sy) in obstacles:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    best = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        # Prefer resources we can reach no later than opponent; break ties by closeness.
        score = (do - ds, -ds, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, rx, ry)
    if best is None:
        return [0, 0]
    _, tx, ty = best

    # If already on target, stay.
    if (sx, sy) == (tx, ty):
        return [0, 0]

    best_step = None
    # Deterministic tie-breaking: fixed move order + score order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = dist((nx, ny), (tx, ty))
        no = dist((ox, oy), (tx, ty))
        step_score = (no - ns, -ns, dx, dy)
        if best_step is None or step_score > best_step[0]:
            best_step = (step_score, dx, dy)

    if best_step is None:
        return [0, 0]
    return [best_step[1], best_step[2]]