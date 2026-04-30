def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    seen = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles and (x, y) not in seen:
                resources.append((x, y))
                seen.add((x, y))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist_cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # If no resources, drift away from opponent while staying safe
        best = (0, 0)
        bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not in_bounds(nx, ny) or (nx, ny) in obstacles:
                continue
            # Prefer increasing distance to opponent; tie-break by closeness to board center
            dk = dist_cheb((nx, ny), (ox, oy))
            ck = -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)
            k = (dk, ck, nx, ny)
            if bestk is None or k > bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Choose move that maximizes our advantage on the "most contested" resource.
    # Advantage on resource r: (opp_dist - my_dist). Also add small tie-break toward nearer resources.
    center = ((w - 1) / 2, (h - 1) / 2)
    best_move = (0, 0)
    best_key = None
    res_list = resources  # already deterministic order from observation
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)

        # Compute best contested gain; also penalize moving too close to opponent (to avoid being mirrored).
        best_gain = None
        best_near = None
        for r in res_list:
            myd = dist_cheb(my_pos, r)
            opd = dist_cheb((ox, oy), r)
            gain = opd - myd
            near = -myd
            key2 = (gain, near, r[0], r[1])
            if best_gain is None or key2 > (best_gain, best_near, r[0], r[1]):
                best_gain = gain
                best_near = near

        # Primary: maximize best_gain. Secondary: maximize near (closer to a contested target).
        # Tertiary: keep distance from opponent to reduce giving them options.
        opp_d = dist_cheb(my_pos, (ox, oy))
        center_bias = -(abs(nx - center[0]) + abs(ny - center[1]))
        k = (best_gain, best_near, opp_d, center_bias, nx, ny)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]