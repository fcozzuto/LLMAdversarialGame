def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev (diagonal-friendly)

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If late game, favor shortest win path; earlier, favor advantage.
    w_adv = 1 if turns_remaining < 10 else 2

    # Precompute for speed
    res_list = []
    for rx, ry in resources:
        if isinstance(rx, int) and isinstance(ry, int):
            res_list.append((rx, ry))

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        immediate = 1 if any(nx == rx and ny == ry for rx, ry in res_list) else 0
        if immediate:
            # Capturing beats everything deterministically
            return [dxm, dym]

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in res_list:
            d_my = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            if d_my < my_best:
                my_best = d_my
            if d_opp < opp_best:
                opp_best = d_opp

        # Heuristic: maximize (opponent lead I can steal), then minimize my distance,
        # and avoid letting opponent get closer to any resource than me.
        opp_can = opp_best - my_best
        block = 0
        for rx, ry in res_list:
            d_my = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            if d_opp + w_adv <= d_my:
                block += 1

        val = (opp_can * 1000) - (my_best * 10) - (block * 50)
        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [best_move[0], best_move[1]]