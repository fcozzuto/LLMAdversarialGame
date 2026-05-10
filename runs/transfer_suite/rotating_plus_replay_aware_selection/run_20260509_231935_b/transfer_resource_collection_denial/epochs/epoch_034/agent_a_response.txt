def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)
    res_set = set((p[0], p[1]) for p in resources)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res_set and (nx, ny) not in obstacles:
            return [dx, dy]

    if not resources:
        return [0, 0]

    # Choose move that best improves our approach to a good target, while keeping opponent farther
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # If we would "accidentally" step onto a resource (should be caught above), prioritize it
        if (nx, ny) in res_set:
            return [dx, dy]

        # Pick target resource from next position by deterministic heuristic
        best_target = None
        best_tkey = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer smaller ds and larger (do-ds); tie-break by lexicographic position
            tkey = (ds - do * 0.25, ds, rx, ry)
            if best_tkey is None or tkey < best_tkey:
                best_tkey = tkey
                best_target = (rx, ry)

        if best_target is None:
            continue
        rx, ry = best_target
        ds = cheb(nx, ny, rx, ry)
        do = cheb(ox, oy, rx, ry)

        # Value: maximize closeness advantage vs opponent; slight penalty for moving away from current best
        # Also nudge toward lower coordinates deterministically on ties.
        val = (do - ds) * 100 - ds
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            if (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]