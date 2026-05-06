def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    # Prefer interceptor-ish play: choose a move that increases relative reach to a nearby resource
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        move_score = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            cur_my = cheb(sx, sy, rx, ry)

            # If opponent is already at/near the resource, discourage (avoid "edge_patrol" contention)
            if opd <= myd + 1:
                continue

            # Reward outpacing opponent and getting closer
            progress = cur_my - myd
            s = (opd - myd) * 30 + progress * 8 - myd

            # Small incentive to take resources that are "open" (not surrounded by obstacles)
            # (kept lightweight; based on 8-neighborhood occupancy)
            open_bonus = 0
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                px, py = nx + ax, ny + ay
                if inb(px, py) and (px, py) not in obstacles:
                    open_bonus += 1
            s += open_bonus

            if s > move_score:
                move_score = s

        # If no "safe" resource found, fall back to moving toward the closest resource,
        # but prefer moves that don't let the opponent get strictly closer to every resource.
        if move_score == -10**18:
            fallback = 0
            my_best = 10**9
            op_best = 10**9
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < my_best:
                    my_best = myd
                if opd < op_best:
                    op_best = opd
            # Lower my_best is better; also avoid worsening relative position too much
            fallback = -my_best * 10 + (op_best - my_best) * 2
            move_score = fallback

        # Deterministic tie-break: prefer moves that are "more diagonal/edge-consistent" (stable ordering)
        if move_score > best_score:
            best_score = move_score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]