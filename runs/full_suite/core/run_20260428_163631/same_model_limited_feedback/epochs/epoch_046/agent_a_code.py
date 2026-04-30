def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    cand_deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose a resource that we can reach relatively earlier than the opponent.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = dist((sx, sy), (rx, ry))
            opd = dist((ox, oy), (rx, ry))
            # Maximize our advantage; if tied, minimize our distance.
            key = (opd - myd, -myd)
            if best is None or key > best_key:
                best = (rx, ry)
                best_key = key
        tx, ty = best
    else:
        # No resources: head to farthest corner from opponent deterministically.
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: dist((ox, oy), c))

    # Move one step toward target while keeping distance from opponent and avoiding obstacles.
    best_move = (0, 0)
    best_score = None
    opp_close = dist((sx, sy), (ox, oy)) <= 1

    for dx, dy in cand_deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_to_t = abs(nx - tx) + abs(ny - ty)
        opp_to_next = abs(nx - ox) + abs(ny - oy)
        # If opponent is adjacent, prioritize backing off.
        score = -my_to_t + 0.25 * opp_to_next
        if opp_close:
            score = 2.0 * opp_to_next - my_to_t
        # Deterministic tie-breaker: prefer smaller dx, then smaller dy.
        key = (score, -opp_to_next, -(-dx), -(-dy), -((nx - tx) == 0 and (ny - ty) == 0))
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]