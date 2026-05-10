def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

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
            val = our_d - 0.95 * opp_d
            if best is None or val < best[0] or (val == best[0] and (rx, ry) < best[1]):
                best = (val, (rx, ry))
        tx, ty = best[1]

    resources_set = set((p[0], p[1]) for p in resources)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        if (nx, ny) in resources_set:
            score = 10**9 - cheb(nx, ny, ox, oy) - 0.1 * cheb(nx, ny, tx, ty)
        else:
            our_to_t = cheb(nx, ny, tx, ty)
            opp_to_t = cheb(ox, oy, tx, ty)
            our_adv = cheb(nx, ny, ox, oy) - cheb(ox, oy, nx, ny)
            score = (-our_to_t) + 0.15 * (opp_to_t - our_to_t) - 0.001 * cheb(nx, ny, tx, ty) + 0.01 * (-our_adv)

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]