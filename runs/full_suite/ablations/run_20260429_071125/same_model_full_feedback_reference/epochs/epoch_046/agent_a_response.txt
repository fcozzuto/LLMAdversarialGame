def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    # If no resources, drift to reduce distance to center and avoid obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_s = -10**9
        best_m = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if -d > best_s:
                best_s = -d
                best_m = (dx, dy)
        return [best_m[0], best_m[1]]

    # Choose move that improves our "advantage" on a resource: (our_dist - k*opp_dist)
    k = 0.85
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Select a target deterministically under this move.
        best_target = None
        best_adv = 10**18
        for rx, ry in resources:
            d_self = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            adv = d_self - k * d_opp  # lower means more favorable
            if adv < best_adv:
                best_adv = adv
                best_target = (rx, ry)

        rx, ry = best_target
        d_self_now = cheb(nx, ny, rx, ry)
        d_self_prev = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)

        # Value: strongly prefer getting closer; also prefer resources where opponent is far.
        val = 3.0 * (d_self_prev - d_self_now) + 0.9 * d_opp - 0.25 * d_self_now
        # Small tie-breaker toward center to diversify paths deterministically.
        center_bias = -0.01 * cheb(nx, ny, (w - 1) / 2.0, (h - 1) / 2.0)
        val += center_bias

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]