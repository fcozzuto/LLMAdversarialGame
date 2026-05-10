def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Deterministic ordering of resources for tie-breaks
    res = sorted((int(r[0]), int(r[1])) for r in resources)

    # Late-game: prioritize closest resource we can take soon; early: prioritize stealing (advantage)
    turns_remaining = observation.get("turns_remaining", 0)
    late = 1 if turns_remaining <= 10 else 0

    def score_pos(mx, my):
        best_adv = -10**9
        best_my_d = 10**9
        best_rx = None
        for rx, ry in res:
            my_d = cheb(mx, my, rx, ry)
            op_d = cheb(ox, oy, rx, ry)
            adv = op_d - my_d  # positive means we are closer
            # Late: mostly minimize my_d; Early: maximize adv, but still prefer small my_d when tied.
            if late:
                primary = -my_d * 1000 + adv
            else:
                primary = adv * 1000 - my_d
            if primary > best_adv or (primary == best_adv and (my_d < best_my_d or (my_d == best_my_d and (rx, ry) < (best_rx if best_rx else (10**9, 10**9))))):
                best_adv = primary
                best_my_d = my_d
                best_rx = (rx, ry)

        # Small penalty for moving into a tight/blocked area to reduce "wasting" moves
        # Count how many adjacent cells are legal (including staying).
        free = 0
        for dx, dy in moves:
            nx, ny = mx + dx, my + dy
            if ok(nx, ny):
                free += 1
        # Encourage movement when not late (but never into blocked)
        return best_adv + (free * (2 if not late else 1))

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy  # engine would keep us in place on invalid move
        sc = score_pos(nx, ny)
        if sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]