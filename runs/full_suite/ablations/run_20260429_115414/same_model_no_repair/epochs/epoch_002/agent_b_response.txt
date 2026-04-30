def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if not resources:
        target = ((w - 1) / 2.0, (h - 1) / 2.0)
        best = None
        bestv = None
        for dx, dy, nx, ny in cand:
            v = cheb((nx, ny), target)
            if bestv is None or v < bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_score = None
    best_move = None
    for dx, dy, nx, ny in cand:
        # Penalty for being adjacent to obstacles (deterministic obstacle-avoidance)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if (xx, yy) in obstacles:
                    adj_obs += 1
        # Choose the resource that gives us best relative advantage from this next position
        best_rel = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_self = cheb((nx, ny), (rx, ry))
            d_opp = cheb((ox, oy), (rx, ry))
            # Prefer resources where we are closer than opponent; also break ties toward nearer to our move.
            rel = (d_self - d_opp, d_self, (abs(rx - nx) + abs(ry - ny)))
            if best_rel is None or rel < best_rel:
                best_rel = rel
        # Higher is worse; compute a scalar to minimize.
        # Also lightly prefer moving toward the chosen resource.
        rel_adv, d_self_min, man = best_rel
        # If we step onto a resource, strongly favor it.
        step_on = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        v = (rel_adv * 10) + d_self_min + 0.1 * man + (0.6 * adj_obs) - (15 * step_on)
        # If we are about to block our opponent indirectly, reward moves that increase their distance to the best resource by more.
        # Approx: compare current vs next distances to our currently preferred resource proxy (resource minimizing d_self-d_opp).
        # Deterministic: use the same best_rel resource (first arg in best_rel search).
        # Since we didn't store which resource it is, approximate using current min of opponent distance to our best target set.
        # Keep it simple and stable: add mid preference to avoid getting stuck.
        mid_pref = cheb((nx, ny), ((w - 1) / 2.0, (h - 1) / 2.0)) * 0.01
        v += mid_pref

        if best_score is None or v < best_score or (v == best_score and (dx, dy) < best_move):
            best_score = v
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]