def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if (d, dx, dy) < best:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[0] != 10**9 else [0, 0]

    res_set = set(tuple(r) for r in resources)

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Prefer immediate pickup.
        if (nx, ny) in res_set:
            base = 10**12
        else:
            base = 0

        # Evaluate best resource from this next cell.
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            myd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Advantage: pick targets opponent is less able to reach.
            adv = (oppd - myd)
            # Slight bias to reduce travel time after advantage.
            val = adv * 1000 - myd
            if val > local_best:
                local_best = val

        # Penalize stepping into cells adjacent to obstacles (soft avoidance).
        # (Uses only local check, deterministic, cheap.)
        adj_pen = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            ax, ay = nx + ddx, ny + ddy
            if (ax, ay) in obstacles:
                adj_pen += 1

        score = base + local_best - adj_pen
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]