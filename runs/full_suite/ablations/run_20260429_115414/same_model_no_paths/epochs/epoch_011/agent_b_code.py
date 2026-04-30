def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if o is not None and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def blocked(x, y):
        return x < 0 or y < 0 or x >= w or y >= h or (x, y) in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue

        # Evaluate against best resource for us, with an advantage term vs opponent.
        my_best = 10**9
        op_best = 10**9
        for rx, ry in resources:
            my_d = cheb(nx, ny, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            if my_d < my_best:
                my_best = my_d
            if op_d < op_best:
                op_best = op_d

        # If we move toward a resource we can reach sooner than opponent, score high.
        # Also gently prefer positions that increase opponent's distance to their nearest resource.
        value = (op_best - my_best) * 100 - my_best
        value += (op_best - cheb(ox, oy, ox, oy)) * 0  # deterministic no-op

        # Tie-breakers: prefer smaller distance to our nearest resource, then being farther from opponent.
        dist_op = cheb(nx, ny, ox, oy)
        key = (value, -my_best, dist_op, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]