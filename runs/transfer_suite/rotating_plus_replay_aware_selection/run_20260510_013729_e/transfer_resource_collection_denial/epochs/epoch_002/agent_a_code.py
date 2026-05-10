def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obstacle_set = set((x, y) for x, y in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def steps(a, b):
        ax, ay = a
        bx, by = b
        dx = abs(bx - ax)
        dy = abs(by - ay)
        return dx if dx > dy else dy  # Chebyshev for 8-dir moves

    def nearest_res_dist(pos):
        if not resources:
            return 0, None
        best_d = None
        best_r = None
        for r in resources:
            d = steps(pos, r)
            if best_d is None or d < best_d or (d == best_d and r < best_r):
                best_d = d
                best_r = r
        return best_d, best_r

    myd, mytarget = nearest_res_dist((sx, sy))
    od, _ = nearest_res_dist((ox, oy))

    if mytarget is None:
        mytarget = (w // 2, h // 2)

    # Evaluate candidate moves: minimize (my distance to target, my chance worse than opponent).
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    desired_dx = 0 if mytarget[0] == sx else (1 if mytarget[0] > sx else -1)
    desired_dy = 0 if mytarget[1] == sy else (1 if mytarget[1] > sy else -1)

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacle_set:
            continue

        tdist = steps((nx, ny), mytarget)

        # Opponent pressure: compare how soon they can reach the same target after our move.
        opp_to_target = steps((ox, oy), mytarget)
        # If we can arrive in fewer steps than opponent, prioritize strongly.
        win_margin = opp_to_target - tdist  # positive is good

        # Also consider overall nearest resource distance for us and opponent.
        n_my_d, _ = nearest_res_dist((nx, ny))
        n_op_d, _ = nearest_res_dist((ox, oy))
        rel = (n_op_d - n_my_d)  # positive means we are closer overall

        align = 0 if (dx == desired_dx and dy == desired_dy) else 1
        # Tie-break deterministically by position and move.
        key = (
            -win_margin,          # larger margin first
            -rel,                 # larger relative closeness first
            tdist,
            align,
            nx,
            ny,
            dx,
            dy,
        )
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]