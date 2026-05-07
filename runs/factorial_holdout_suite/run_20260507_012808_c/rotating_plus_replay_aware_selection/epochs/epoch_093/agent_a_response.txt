def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    res = sorted((int(x), int(y)) for x, y in resources)  # deterministic
    # Only consider a few closest resources to keep deterministic and fast
    near = sorted(res, key=lambda p: cheb(sx, sy, p[0], p[1]))[:8]

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        move_score = -10**18
        for rx, ry in near:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer getting closer to a resource that is relatively farther from opponent.
            s = (opp_d - our_d) * 1000 - our_d
            # Slightly prefer moves that reduce our distance to the currently-nearest resource.
            cur_near = near[0]
            s += (cheb(sx, sy, cur_near[0], cur_near[1]) - cheb(nx, ny, cur_near[0], cur_near[1]))
            # If we can land on a resource, prioritize heavily.
            if (nx, ny) == (rx, ry):
                s += 10**7
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]
    return best_move