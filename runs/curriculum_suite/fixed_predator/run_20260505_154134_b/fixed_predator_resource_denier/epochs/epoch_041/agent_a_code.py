def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set(tuple(p) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Candidate neighbors (stay allowed)
    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best = [0, 0]
    best_key = None

    # Heuristic: move to reduce our distance to the most attainable resource, while not giving opponent the same access.
    # We approximate opponent "access" by their distance to the same resource.
    alpha = 1.15
    gamma = 0.15  # mild bias to central area when tied

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        # Find best resource for us after this move
        local_best = None
        local_key = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner than opponent; tie-break by raw ds then by position.
            # Key uses ascending order.
            k = (alpha * do - ds, ds, rx + ry, rx, ry)
            if local_key is None or k < local_key:
                local_key = k
                local_best = (rx, ry, ds, do)

        if local_best is None:
            continue

        rx, ry, ds, do = local_best
        # Global score key: primary minimize (alpha*do - ds), secondary minimize ds,
        # tertiary prefer being closer to center; finally tie-break by position.
        center_bonus = cheb(nx, ny, w // 2, h // 2)
        key = (local_key[0], local_key[1], int(gamma * center_bonus), local_best[3], rx + ry, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best