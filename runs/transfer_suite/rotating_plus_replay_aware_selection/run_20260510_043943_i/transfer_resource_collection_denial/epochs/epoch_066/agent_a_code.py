def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cell_ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    def d(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diag-allowed)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            nx, ny = sx, sy

        # Choose the resource that maximizes our lead after this move.
        # Key: (lead, -self_dist, resource_x, resource_y)
        best_key = None
        chosen = None
        for rx, ry in resources:
            if not cell_ok(rx, ry):
                continue
            sd = d(nx, ny, rx, ry)
            od = d(ox, oy, rx, ry)
            lead = od - sd  # positive means we are closer
            key = (lead, -sd, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                chosen = (rx, ry)

        # Now choose move by resulting best_key, then by proximity.
        if best_key is None:
            continue
        move_key = best_key
        # Secondary tie: prefer moves that reduce distance to the currently best resource.
        if chosen is not None:
            msd = d(nx, ny, chosen[0], chosen[1])
            move_key = (move_key[0], move_key[1], -msd, chosen[0], chosen[1])
        else:
            move_key = (move_key[0], move_key[1], 0, 0, 0)

        if best is None or move_key > best:
            best = move_key
            best_move = (nx - sx, ny - sy)

    return [int(best_move[0]), int(best_move[1])]