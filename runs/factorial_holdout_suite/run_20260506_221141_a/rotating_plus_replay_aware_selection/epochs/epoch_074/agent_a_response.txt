def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx = gw - 1 if sx < gw // 2 else 0
        ty = gh - 1 if sy < gh // 2 else 0
        best = [0, 0]
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -cheb(nx, ny, tx, ty)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**18

    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not legal(nx, ny):
            continue

        my_best = -10**18
        for rx, ry in resources:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_opp - d_me  # positive means we reach earlier (or same time if 0)
            # Prefer strongly winning grabs; otherwise prefer decreasing our time and blocking closer resources.
            v = adv * 100 - d_me
            if v > my_best:
                my_best = v

        # Small bias toward being closer to any resource (reduces dithering)
        closeness = 10 - min(cheb(nx, ny, rx, ry) for rx, ry in resources)
        total = my_best + closeness
        if total > best_val:
            best_val = total
            best_move = [dxm, dym]

    return best_move