def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx >= dy else dy

    def step_ok(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def obs_pen(x, y):
        if not obs:
            return 0
        pen = 0
        for ax, ay in obs:
            d = abs(x - ax) + abs(y - ay)
            if d == 0:
                return 10**6
            pen += 6 - (6 if d >= 6 else d)  # 0..5-ish, closer -> larger
        return pen

    # Pick target: prioritize resources we can reach first (by Chebyshev), with tie-breaks for closer and more centered.
    if res:
        best = None
        for rx, ry in res:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Higher is better
            score = (do - ds) * 1000 - ds * 10 + (3 - abs(rx - (w - 1) / 2.0)) - (3 - abs(ry - (h - 1) / 2.0))
            key = (score, -ds, -rx, -ry)
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not step_ok(nx, ny):
            continue

        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)

        # Want to get on a line that wins the resource race; also avoid tight obstacle neighborhoods.
        # Strongly prefer moves that reduce our distance to target and increase opponent's relative standing.
        rel = (do - ds)
        forward = -(abs(nx - tx) + abs(ny - ty))
        score = rel * 2000 - ds * 25 + forward * 2 - obs_pen(nx, ny)

        # Deterministic tie-break: prefer smaller dx/dy magnitude then lexicographic.
        tie = (-abs(dx) - abs(dy), -dx, -dy)
        score2 = (score, tie)

        if score2 > (best_score, (0, 0, 0)):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]