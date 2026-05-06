def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Pick a resource that the opponent is currently closer to (to contest/deny).
    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = dist(sx, sy, rx, ry)
        opd = dist(ox, oy, rx, ry)
        key = (-(opd - myd), myd)  # maximize (opd - myd), then minimize myd
        # If opponent isn't closer, still allow it but with lower priority.
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    if (sx, sy) == (rx, ry):
        # Stay to secure if allowed; otherwise, avoid obstacles by moving to a safe neighbor.
        for dx, dy in [(0, 0)] + moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]

    # Choose move that best advances toward the contested resource while keeping distance from opponent.
    best_move = [0, 0]
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd_next = dist(nx, ny, rx, ry)
        opd_next = dist(nx, ny, ox, oy)
        val = (myd_next, -opd_next, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move