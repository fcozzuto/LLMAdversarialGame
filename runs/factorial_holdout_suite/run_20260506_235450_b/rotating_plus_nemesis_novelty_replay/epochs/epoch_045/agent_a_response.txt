def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not resources:
        tx, ty = w - 1, h - 1
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for mx, my in cand:
            if valid(sx + mx, sy + my):
                return [mx, my]
        return [0, 0]

    best_move = (0, 0)
    best_score = (-10**9, 10**9, 0, 0)

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate move by the best resource we can secure this turn horizon (distance-based).
        move_best = (-10**9, 10**9, 0, 0)
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            advantage = opp_d - self_d  # positive means we are closer
            # Prefer securing advantage; then nearer; then deterministically by coordinates.
            sc = (advantage, -self_d, -rx, -ry)
            if sc > move_best:
                move_best = sc
        if move_best > best_score:
            best_score = move_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]