def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def time_to(x, y, tx, ty):
        # diagonal moves allowed; Chebyshev time is tight and deterministic
        dx = x - tx
        dy = y - ty
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Pick a target where we have the biggest lead (or smallest loss), deterministically.
    best = None
    best_key = None
    for rx, ry in resources:
        my_t = time_to(sx, sy, rx, ry)
        op_t = time_to(ox, oy, rx, ry)
        # Larger lead is better; if tie, smaller my_t, then prefer "more central" via coordinates.
        key = (op_t - my_t, -my_t, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    rx, ry = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Also consider a second target to avoid getting trapped into a losing chase.
    sec = None
    sec_key = None
    for r2x, r2y in resources:
        if (r2x, r2y) == (rx, ry):
            continue
        my_t = time_to(sx, sy, r2x, r2y)
        op_t = time_to(ox, oy, r2x, r2y)
        key = (op_t - my_t, -my_t, -r2x, -r2y)
        if sec_key is None or key > sec_key:
            sec_key = key
            sec = (r2x, r2y)

    def eval_pos(nx, ny):
        # Main: reduce our time to best target and increase opponent's time.
        my_t1 = time_to(nx, ny, rx, ry)
        op_t1 = time_to(ox, oy, rx, ry)
        # Secondary: if we can't beat best soon, use second target to pivot.
        my_t2 = 10**9
        if sec is not None:
            r2x, r2y = sec
            my_t2 = time_to(nx, ny, r2x, r2y)
        my_t = my_t1 if my_t1 <= my_t2 else my_t2

        # Discourage moves adjacent to opponent (risk of being contested/lost tempo).
        dist_opp = abs(nx - ox)
        d2 = abs(ny - oy)
        dist_opp = dist_opp if dist_opp > d2 else d2  # Chebyshev adjacency proxy

        # Mild obstacle pressure: avoid "tight corners" by slightly penalizing low mobility.
        tight = 0
        for dx, dy in moves:
            ax, ay = nx + dx, ny + dy
            if in_bounds(ax, ay) and (ax, ay) not in obstacles:
                tight += 1
        mobility = tight

        # Score higher is better.
        score = 0
        score += (20 - my_t) * 10
        score += (op_t1 - my_t1) * 6  # try to preserve/extend lead
        if dist_opp <= 1:
            score -= 35
        score += mobility  # keep moving
        return score

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        sc = eval_pos(nx, ny)
        if best_score is