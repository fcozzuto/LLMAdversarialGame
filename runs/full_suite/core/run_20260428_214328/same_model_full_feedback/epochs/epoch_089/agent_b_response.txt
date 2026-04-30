def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def move_score(nx, ny):
        if (nx, ny) in obstacles or not ok(nx, ny):
            return -10**9
        # If moving onto a resource, prioritize heavily.
        if (nx, ny) in set(resources):
            return 10**6
        if not resources:
            # Drift toward center if no visible resources.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            return -(abs(nx - cx) + abs(ny - cy))
        # Prefer resources where we are closer than opponent, and which are nearer overall.
        # Deterministic: tie-break via lexicographic resource ordering handled by fixed iteration.
        best = -10**18
        for rx, ry in resources:
            dm = cheb(nx, ny, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            # Relative advantage + distance pressure (faster pickups first).
            val = (dop - dm) * 1000 - dm
            if (rx, ry) == resources[0]:
                pass
            if val > best:
                best = val
        return best

    # Deterministic tie-break: fixed dir order already.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = move_score(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]