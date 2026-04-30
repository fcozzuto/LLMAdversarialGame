def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    res_set = {(x, y) for x, y in resources}
    if (sx, sy) in res_set:
        return [0, 0]

    obs = {(x, y) for x, y in obstacles}
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose a move that maximizes our distance advantage to the best target resource.
    best_choice = None  # (score_tuple, dx, dy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue

        best_adv = -10**9
        best_myd = 10**9
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd  # positive means we are closer than opponent
            if adv > best_adv or (adv == best_adv and myd < best_myd):
                best_adv = adv
                best_myd = myd

        # Score favors higher advantage; tie-break by smaller distance to that chosen resource,
        # then by staying/moving minimally for determinism.
        score = (best_adv, -best_myd, -abs(dx) - abs(dy))
        if best_choice is None or score > best_choice[0]:
            best_choice = (score, dx, dy)

    if best_choice is None:
        return [0, 0]
    return [best_choice[1], best_choice[2]]