def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w // 2, h // 2
        best = [0, 0]
        bestd = 10**9
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (mx, my) < (best[0], best[1])):
                bestd = d
                best = [mx, my]
        return best

    # Deterministic: evaluate next-step "advantage" on nearest/best resource.
    best = [0, 0]
    best_val = -10**18
    t = int(observation.get("turn_index", 0))

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue

        # Choose the resource that yields max advantage for this next cell.
        local_best = -10**18
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach earlier; also prefer being closer and more "tempo" for denier.
            val = (od - sd) * 1000 - sd
            # Tiny deterministic tie-break: based on coordinates and turn index.
            val += ((rx * 31 + ry * 17 + t) % 7) * 0.001
            if val > local_best:
                local_best = val
        # Prefer move that gives higher local_best; tie-break deterministically by (move).
        if local_best > best_val or (local_best == best_val and (mx, my) < (best[0], best[1])):
            best_val = local_best
            best = [mx, my]

    return best