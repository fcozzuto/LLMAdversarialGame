def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        return [0, 0]

    # Identify opponent's likely target (nearest remaining resource).
    tx, ty = resources[0]
    best_td = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < best_td:
            best_td, tx, ty = d, rx, ry

    my_near_x, my_near_y = resources[0]
    my_best_d = 10**9
    for rx, ry in resources:
        d = man(sx, sy, rx, ry)
        if d < my_best_d:
            my_best_d, my_near_x, my_near_y = d, rx, ry

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        my_d_near = man(nx, ny, my_near_x, my_near_y)
        opp_d_near = man(ox, oy, my_near_x, my_near_y)

        # Contest opponent's nearest target more aggressively.
        my_d_t = man(nx, ny, tx, ty)
        opp_d_t = man(ox, oy, tx, ty)

        # Discourage giving opponent a free path by worsening their access to top target.
        score = 0
        score += (opp_d_near - my_d_near) * 4
        score += (opp_d_t - my_d_t) * 6

        # Keep pressure: reduce distance to opponent's target.
        score -= my_d_t * 0.6

        # Center bias (helps against center_rush archetype).
        score += -0.2 * (man(nx, ny, int(cx), int(cy)))

        # Safety: avoid stagnation unless it's also best for contesting.
        if (dx, dy) == (0, 0):
            score -= 0.5 + 0.2 * (my_d_t - man(sx, sy, tx, ty))

        # Slight penalty if we abandon our own nearest resource too much.
        cur_my_near = my_best_d
        score += (cur_my_near - my_d_near) * 1.5

        # Deterministic tie-break.
        key = (-score, man(nx, ny, my_near_x, my_near_y), man(nx, ny, tx, ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]