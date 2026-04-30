def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # deterministic "hold center, sidestep opponent"
            score = cheb(nx, ny, cx, cy) - 0.5 * cheb(nx, ny, ox, oy)
            key = (score, nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate this move by selecting the best "intercept" resource.
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_now = cheb(nx, ny, rx, ry)
            op_now = cheb(ox, oy, rx, ry)
            my_can = 0 if my_now <= 1 else my_now - 1
            op_can = 0 if op_now <= 1 else op_now - 1

            # If I can take it next step while opponent can't, prioritize heavily.
            can_take_me = (my_now == 1 or my_now == 0) and (op_now > 1)
            can_take_them = (op_now == 1 or op_now == 0) and (my_now > 1)

            advantage = op_can - my_can  # positive is good (opponent farther after 1 step)
            # Extra bias toward resources that are currently closer to me (not just "advantage").
            closeness = op_now - my_now

            # Key: maximize advantage/closeness, but avoid moves that let opponent a clear next take.
            score = advantage * 6 + closeness * 2
            if can_take_me:
                score += 50
            if can_take_them:
                score -= 35

            # Deterministic tie-breakers: prefer lower my distance, then lexicographic position.
            key = (-score, my_now, nx, ny)
            if local_best is None or