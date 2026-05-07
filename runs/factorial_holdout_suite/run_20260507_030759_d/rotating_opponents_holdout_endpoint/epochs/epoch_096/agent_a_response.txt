def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    # Move selection: maximize advantage over opponent for the "best" resource, with small tie-breakers.
    best = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        total = 0.0
        for rx, ry in resources:
            if not ok(rx, ry):
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # advantage: positive when we are closer (or equal), plus mild incentive to reduce our distance
            total += (do - ds) + (0.05 / (1 + ds))
        # If we can't improve much, still prefer reducing distance to nearest resource
        if total == 0.0:
            # nearest distance heuristic
            nearest = 10**9
            for rx, ry in resources:
                if ok(rx, ry):
                    d = cheb(nx, ny, rx, ry)
                    if d < nearest:
                        nearest = d
            total = -nearest

        # Deterministic tie-break: lexicographic on (score, dx, dy)
        if best_score is None or total > best_score or (total == best_score and (dx, dy) < best):
            best_score = total
            best = (dx, dy)

    return [int(best[0]), int(best[1])]