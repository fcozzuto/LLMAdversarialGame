def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Select target: prioritize resources we can reach earlier; otherwise deny opponent the best one.
    target = None
    best = None
    for r in resources:
        if not isinstance(r, (list, tuple)) or len(r) < 2:
            continue
        rx, ry = r[0], r[1]
        if not isinstance(rx, int) or not isinstance(ry, int):
            continue
        if not valid(rx, ry):
            continue
        dme = cheb((sx, sy), (rx, ry))
        doe = cheb((ox, oy), (rx, ry))
        lead = doe - dme  # positive means we are closer in time
        # Tiebreak: prefer smaller self distance then larger lead, then closer to opponent (to contest earlier pathing)
        key = (lead, -dme, -doe, -rx, -ry)
        if best is None or key > best:
            best = key
            target = (rx, ry)

    if target is None:
        return [0, 0]

    tx, ty = target
    # Greedy one-step lookahead: choose move that improves (lead, closeness) toward target.
    cur_lead = cheb((sx, sy), (tx, ty)) - cheb((ox, oy), (tx, ty))
    # We want dme <= doe, i.e. lead = doe - dme large. Equivalent minimize self_time - opp_time.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dme = cheb((nx, ny), (tx, ty))
        doe = cheb((ox, oy), (tx, ty))
        lead = doe - dme
        # Small preference for moves closer to target and avoid wasting when already equal.
        key = (lead, -dme, abs(nx - sx) + abs(ny - sy), -(cheb((nx, ny), (ox, oy))))
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]