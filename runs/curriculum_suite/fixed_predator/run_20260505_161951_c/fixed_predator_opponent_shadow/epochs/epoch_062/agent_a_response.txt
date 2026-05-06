def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        # Go toward the middle while biasing away from opponent to keep control.
        tx, ty = (sx + ox) // 2, (sy + oy) // 2
        best = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            val = (man((nx, ny), (tx, ty)), -man((nx, ny), (ox, oy)))
            if best is None or val < best[0]:
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    # Choose move that creates the largest "reach advantage" to some resource, with tie-breakers.
    best_move = (0, 0)
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        my_dist = abs(nx - ox) + abs(ny - oy)  # separation proxy
        # Evaluate best resource from this next position.
        best_r = None
        best_r_key = None
        for rx, ry in resources:
            d_self = abs(nx - rx) + abs(ny - ry)
            d_opp = abs(ox - rx) + abs(oy - ry)
            reach_adv = d_opp - d_self  # positive means we arrive sooner (or tie favored)
            # Prefer smaller self distance to finish, also prefer immediate pickup proximity.
            key = (-(reach_adv), d_self, -d_opp, abs(nx - rx) + abs(ny - ry) == 0)
            if best_r_key is None or key < best_r_key:
                best_r_key = key
                best_r = (reach_adv, d_self, d_opp)
        # For overall move: maximize reach advantage first, then improve self progress,
        # then maintain some distance from opponent.
        reach_adv, d_self, d_opp = best_r
        overall = (-reach_adv, d_self, -my_dist, d_opp)
        if best_key is None or overall < best_key:
            best_key = overall
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]