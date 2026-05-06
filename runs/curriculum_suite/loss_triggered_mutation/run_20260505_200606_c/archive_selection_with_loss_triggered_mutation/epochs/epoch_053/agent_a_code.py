def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # If no resources, head toward center deterministically (avoid obstacles).
    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (-dist((nx, ny), (tx, ty)), nx, ny)
            if best is None or key > best[0]:
                best = (key, (dx, dy))
        return best[1] if best else [0, 0]

    # Choose move that maximizes immediate "lead" over opponent for the best contestable resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_for_move = None
        for rx, ry in resources:
            myd = dist((nx, ny), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            lead = opd - myd  # positive means we can reach sooner
            # Secondarily prefer lower myd (closer) and higher coordinate tie-break (deterministic).
            key = (lead, -myd, -rx, -ry)
            if best_for_move is None or key > best_for_move:
                best_for_move = key
        if best_for_move is None:
            continue

        # If all leads are negative, still prefer moves that reduce distance to the most likely resource,
        # with a preference for moving toward center to avoid dead-ends.
        center = (w // 2, h // 2)
        center_bias = -dist((nx, ny), center) * (1 if best_for_move[0] < 0 else 2)
        move_key = (best_for_move[0], best_for_move[1], center_bias, -abs(nx - sx) - abs(ny - sy), -nx, -ny)
        if best is None or move_key > best[0]:
            best = (move_key, (dx, dy))

    return list(best[1]) if best else [0, 0]