def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    occ = set((x, y) for x, y in obstacles)
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # If on a resource, stay to collect
    for rx, ry in resources:
        if rx == sx and ry == sy:
            return [0, 0]

    # Select target: best "steal" opportunity (self closer than opponent)
    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = cheb(sx, sy, rx, ry)
        opp_d = cheb(ox, oy, rx, ry)
        diff = my_d - opp_d  # negative is good (we're closer)
        key = (diff, my_d, opp_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0:
            nx = 0
        elif nx >= w:
            nx = w - 1
        if ny < 0:
            ny = 0
        elif ny >= h:
            ny = h - 1

        if (nx, ny) in occ:
            penalty = 10**6
        else:
            penalty = 0

        my_to_t = cheb(nx, ny, tx, ty)
        opp_to_t = cheb(ox, oy, tx, ty)

        # Encourage cutting off opponent by choosing moves that keep us not too far ahead/behind
        my_vs_opp = my_to_t - opp_to_t

        # Also keep from stepping into positions near many resources (to reduce opponent sweep value)
        near_res = 0
        for rx, ry in resources:
            if cheb(nx, ny, rx, ry) == 0:
                near_res += 1
            elif cheb(nx, ny, rx, ry) == 1:
                near_res += 0.25

        val = (penalty, my_vs_opp, my_to_t, near_res, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move