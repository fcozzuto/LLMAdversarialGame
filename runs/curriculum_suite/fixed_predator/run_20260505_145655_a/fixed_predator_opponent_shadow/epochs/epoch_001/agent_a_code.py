def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    cand = []
    order = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    safe = []
    for dx, dy in order:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        safe.append((dx, dy, nx, ny))

    # Target: nearest resource (if none, just try to evade opponent)
    if resources:
        best_r = None
        best_d = 10**9
        for rx, ry in resources:
            d = dist(x, y, rx, ry)
            if d < best_d:
                best_d = d
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = None, None

    # Predator pressure: if close to opponent, prioritize escape
    opp_close = dist(x, y, ox, oy) <= 3

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in safe:
        score = 0
        if tx is not None:
            score += (dist(x, y, tx, ty) - dist(nx, ny, tx, ty)) * 3  # move toward target
            # small bias: prefer aligning closer to target
            score += -((tx - nx) ** 2 + (ty - ny) ** 2) * 0.01
        d_opp = dist(nx, ny, ox, oy)
        if opp_close:
            score += d_opp * 2.0  # flee
        else:
            # avoid walking directly into opponent too often
            score += d_opp * 0.25
        # If could pick up resource (standing on it), boost heavily
        if resources and (nx, ny) in set(tuple(p) for p in resources):
            score += 1000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]