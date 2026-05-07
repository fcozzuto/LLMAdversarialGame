def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = abs(ax - bx); dy = abs(ay - by)
        return dx if dx > dy else dy

    def clamp_inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res_set = set(tuple(p) for p in resources)
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def best_value(from_x, from_y):
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(from_x, from_y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer than opponent;
            # secondary: prefer immediate reach, avoid far away.
            v = (do - ds) * 1000 + (3000 // (ds + 1)) - (10 * (rx + ry))
            if (rx, ry) == (from_x, from_y):
                v += 10**7
            if v > best:
                best = v
        return best

    # If the opponent is already on a resource, prioritize escaping toward next best.
    # Otherwise, contest the resource that maximizes our advantage after one step.
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not clamp_inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = best_value(nx, ny)
        # Deterministic tie-breaker: prefer smaller step, then lexicographic.
        if sc > best_score or (sc == best_score and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_score = sc
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]