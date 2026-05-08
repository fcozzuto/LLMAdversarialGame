def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    resources = observation.get("resources") or []
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        # Prefer resources we are closer to than opponent; otherwise still pick a promising one.
        best = None
        for rx, ry in resources:
            dS = abs(sx - rx) + abs(sy - ry)
            dO = abs(ox - rx) + abs(oy - ry)
            # Lower key is better: our lead first, then shorter distance to reach.
            key = (-(dO - dS), dS, dO, rx, ry)
            if best is None or key < best[0]:
                best = (key, rx, ry)
        tx, ty = best[1], best[2]

    best_key = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue

        # Evaluate move relative to the contest over resources (only local heuristic).
        # For each next cell, compute the best "advantage" among resources.
        if resources:
            best_adv = None
            for rx, ry in resources:
                dS0 = abs(sx - rx) + abs(sy - ry)
                dO0 = abs(ox - rx) + abs(oy - ry)
                dS1 = abs(nx - rx) + abs(ny - ry)
                dO1 = abs(ox - rx) + abs(oy - ry)

                # Primary: reduce our distance more than it reduces opponent's (opponent fixed here).
                # Secondary: maximize our lead over opponent (dO1 - dS1).
                adv1 = (dO1 - dS1)
                deltaS = dS0 - dS1
                key = (-adv1, -deltaS, dS1, dO1, rx, ry)
                if best_adv is None or key < best_adv[0]:
                    best_adv = (key, adv1, dS1)
            _, adv1, dS1 = best_adv
            # Also nudge toward target position to break ties deterministically.
            to_tgt = abs(nx - tx) + abs(ny - ty)
            key_move = (0, -adv1, to_tgt, dx, dy, nx, ny)
        else:
            d0 = abs(sx - tx) + abs(sy - ty)
            d1 = abs(nx - tx) + abs(ny - ty)
            key_move = (d1, -(d0 - d1), dx, dy, nx, ny)

        if best_key is None or key_move < best_key:
            best_key = key_move
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]