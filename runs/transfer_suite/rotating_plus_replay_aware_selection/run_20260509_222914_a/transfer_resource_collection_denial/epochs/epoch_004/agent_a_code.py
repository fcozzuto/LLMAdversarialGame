def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_val = None
        for rx, ry in resources:
            our_d = cheb(x, y, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we're relatively closer to; slightly prefer those closer overall.
            val = (our_d - 1.15 * opp_d, our_d, rx, ry)
            if best_val is None or val < best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    resources_set = set((p[0], p[1]) for p in resources)
    best_move = (0, 0)
    best_score = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if resources and (nx, ny) in resources_set:
            score = -10**9 + cheb(nx, ny, ox, oy)
        else:
            our_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Greedy toward target, but bias to reduce opponent advantage (denier behavior).
            score = our_d - 1.05 * opp_d + 0.02 * (cheb(nx, ny, w - 1 - ox, h - 1 - oy))

        if best_score is None or score < best_score or (score == best_score and (nx, ny) < (x + best_move[0], y + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]