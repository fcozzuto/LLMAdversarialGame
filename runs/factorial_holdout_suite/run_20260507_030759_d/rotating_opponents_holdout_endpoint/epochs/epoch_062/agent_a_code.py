def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                res.append((x, y))

    if not res:
        return [0, 0]

    moves = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    best_score = -10**18
    best_move = [0, 0]

    # Prefer capturing a resource where we are not behind; otherwise, minimize our distance to the best available.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue

        score = 0
        # Small deterministic bias to prefer moving toward the map center when tied.
        center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * 1e-6

        best_res_term = -10**18
        for rx, ry in res:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # If we can reach at least as fast as opponent, strongly prioritize.
            lead = od - sd
            # Encourage actually going toward closer resources; lead dominates.
            term = lead * 1000 - sd
            if term > best_res_term:
                best_res_term = term

        score = best_res_term + center_bias

        # Deterministic tie-break: prefer staying when equal? We'll prefer smaller dx, then smaller dy.
        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move