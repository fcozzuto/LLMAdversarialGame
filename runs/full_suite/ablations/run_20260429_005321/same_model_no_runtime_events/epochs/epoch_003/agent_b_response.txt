def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set((p[0], p[1]) for p in (observation["obstacles"] or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If opponent can grab a resource immediately, deprioritize it.
    def immediate_opponent_take(rx, ry):
        return max(abs(ox - rx), abs(oy - ry)) == 1

    # Score a move by local advantage over opponent over the best resource after the move.
    best_move = (0, 0)
    best_val = -10**18
    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue

        if not resources:
            dist_center = max(abs(nx - cx), abs(ny - cy))
            dist_opp = max(abs(nx - ox), abs(ny - oy))
            val = -dist_center - 0.05 * dist_opp
        else:
            val = -10**18
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                ds = max(abs(nx - rx), abs(ny - ry))
                do = max(abs(ox - rx), abs(oy - oy))

                # Prefer being closer; penalize if opponent is much closer or can take right away.
                rel = do - ds
                if immediate_opponent_take(rx, ry) and do < ds:
                    rel -= 5

                # Encourage moving along diagonals and toward "useful" resources deterministically.
                bias = 0.001 * (rx * 0.5 + ry) + 0.0001 * (abs(dx) + abs(dy) == 2)
                # If we're winning for a target (ds < do), also prefer it being attainable sooner.
                win_bonus = 0
                if ds < do:
                    win_bonus = 0.02 / (1 + ds)
                val_candidate = rel * 10 - 0.3 * ds + win_bonus + bias
                if val_candidate > val:
                    val = val_candidate

        # Deterministic tie-break: lexicographically smaller move among equals.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]