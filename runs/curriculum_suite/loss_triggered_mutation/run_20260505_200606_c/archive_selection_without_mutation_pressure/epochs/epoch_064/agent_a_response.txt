def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    valid_resources = [(rx, ry) for (rx, ry) in resources if (rx, ry) not in obstacles]
    if not valid_resources:
        return [0, 0]
    resources = valid_resources

    best_r = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Prefer securing (we not farther), then closest secured distance; else closest overall.
        if sd <= od:
            key = (0, sd, od - sd, rx, ry)
        else:
            key = (1, od - sd, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)
    tx, ty = best_r

    # Denier-style: pick move that maximizes our advantage (oppdist - mydist) on scarce top resources.
    top_res = sorted(resources, key=lambda p: cheb(ox, oy, p[0], p[1]))[: min(6, len(resources))]

    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_to_target = cheb(nx, ny, tx, ty)
        opp_to_target = cheb(ox, oy, tx, ty)

        # Advantage over opponent across selected resources.
        adv = 0
        min_adv = None
        for rx, ry in top_res:
            d_my = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            a = d_opp - d_my
            adv += a
            if min_adv is None or a < min_adv:
                min_adv = a

        # Lexicographic: secure target first, then minimize our distance, then maximize advantage.
        secure = 0 if my_to_target <= opp_to_target else 1
        key = (secure, my_to_target, -adv, -(min_adv if min_adv is not None else -10**9), -dx, -dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]