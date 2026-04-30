def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx, dy in dirs:
            if (x + dx, y + dy) in obstacles:
                c += 1
        return c

    def score_cell(x, y):
        if not free(x, y):
            return -10**18
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return -cheb(x, y, tx, ty) - 0.25 * adj_obs(x, y)

        best = -10**18
        for rx, ry in resources:
            d_me = cheb(x, y, rx, ry)
            d_op = cheb(ox, oy, rx, ry)

            # If we can be earlier than opponent, strongly prefer.
            lead = d_op - d_me

            # If opponent is much closer, prefer blocking by moving toward
            # that resource's "frontier" (reducing our distance and their next-step).
            block_term = 0.0
            if d_me > d_op:
                block_term = -0.6 * (d_me - d_op)

            # Avoid stepping into obstacle clusters and avoid being too close to opponent
            # unless it helps secure a lead.
            opp_close = cheb(x, y, ox, oy)
            opp_pen = 0.35 * (1 if opp_close <= 1 else 0) + 0.15 * (1 if opp_close == 2 else 0)

            # Small deterministic bias to avoid ties: prefer resources with higher x then y.
            tie_bias = 0.001 * (rx * 8 + ry)

            v = lead * 12.0 - d_me * 0.45 - adj_obs(rx, ry) * 0.9 + block_term - opp_pen + tie_bias
            if v > best:
                best = v
        return best

    best_moves = []
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        v = score_cell(nx, ny)
        if v > best_val + 1e-12:
            best_val = v
            best_moves = [(dx, dy)]
        elif abs(v - best_val) <= 1e-12:
            best_moves.append((dx, dy))

    # Deterministic tie-break: prefer moves that reduce distance to the closest "currently reachable" lead resource.
    def tie_key(m):
        dx, dy = m
        nx, ny = sx + dx, sy + dy
        # compute min our distance among resources where we are not hopelessly behind
        bestd = 10**9
        if resources:
            for rx, ry in resources:
                d_me = cheb(nx, ny, rx, ry)
                d_op = cheb(ox, oy, rx, ry)
                if d_op - d_me >= 0:
                    if d_me < bestd:
                        bestd = d_me
            if bestd == 10**9:
                for rx, ry in resources:
                    d_me = cheb(nx, ny, rx, ry)
                    if d_me < bestd:
                        bestd = d_me
        else:
            bestd = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        # prefer staying closer to center lightly
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        cent = abs(nx - cx) + abs(ny - cy)
        # prefer non-stay if equal
        stay_pen = 0 if (dx != 0 or dy != 0) else 0.01
        # deterministic secondary using direction order
        dir_pen =