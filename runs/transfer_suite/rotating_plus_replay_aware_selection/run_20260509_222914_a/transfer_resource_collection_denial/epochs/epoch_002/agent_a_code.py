def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles_list = observation["obstacles"] or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1,  0), (0,  0), (1,  0),
              (-1,  1), (0,  1), (1,  1)]

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    if not resources:
        tx, ty = w // 2, h // 2
    else:
        best = None
        for rx, ry in resources:
            our_d = cheb(x, y, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            val = our_d - 0.9 * opp_d
            if best is None or val < best[0] or (val == best[0] and (rx, ry) < best[1]):
                best = (val, (rx, ry))
        tx, ty = best[1]

    resources_set = set((p[0], p[1]) for p in resources)
    best_score = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Strong incentive to collect
        if (nx, ny) in resources_set:
            score = 10000 - cheb(nx, ny, ox, oy)
        else:
            our_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(nx, ny, ox, oy)

            # Relative progress against opponent
            score = -our_d + 0.35 * opp_d

            # Obstacle proximity penalty (avoid getting boxed in)
            near = 0
            for ox2, oy2 in obstacles_list:
                if cheb(nx, ny, ox2, oy2) <= 1:
                    near += 1
            score -= 0.6 * near

            # Mild preference for moving toward target (tie-break against staying)
            score += -0.05 * (1 if (dx, dy) != (0, 0) else 0) * cheb(nx, ny, tx, ty)

        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]