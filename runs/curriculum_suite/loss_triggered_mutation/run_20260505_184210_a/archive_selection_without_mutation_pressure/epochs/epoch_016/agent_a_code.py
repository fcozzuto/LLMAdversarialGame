def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    def best_step(fromx, fromy, tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = fromx + dx, fromy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = cheb(nx, ny, tx, ty)
                key = (d, dx, dy)
                if best is None or key < best:
                    best = key
        if best is None:
            return (0, 0)
        return (best[1], best[2])

    def min_to_resources(x, y):
        if not resources:
            return 10**9
        return min(cheb(x, y, rx, ry) for rx, ry in resources)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            key = (cheb(nx, ny, cx, cy), dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    my_target = min(resources, key=lambda p: (cheb(sx, sy, p[0], p[1]), p[0], p[1]))
    opp_target = min(resources, key=lambda p: (cheb(ox, oy, p[0], p[1]), p[0], p[1]))
    odx, ody = best_step(ox, oy, opp_target[0], opp_target[1])
    opp_next = (ox + odx, oy + ody)

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist_me_to_oppnext = cheb(nx, ny, opp_next[0], opp_next[1])
        dist_me_to_opp_target = cheb(nx, ny, opp_target[0], opp_target[1])
        dist_me_to_my_target = cheb(nx, ny, my_target[0], my_target[1])
        dmin = min_to_resources(nx, ny)

        # Intercept priority: contest opponent's next approach; secondary: keep collecting.
        key = (0,
               dist_me_to_oppnext,
               dist_me_to_my_target,
               dist_me_to_opp_target,
               dmin,
               dx, dy)
        if best is None or key < best:
            best = key

    return [best[-2], best[-1]]