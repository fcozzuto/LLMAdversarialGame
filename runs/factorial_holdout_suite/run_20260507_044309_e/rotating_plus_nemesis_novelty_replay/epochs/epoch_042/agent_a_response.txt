def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obs_raw = observation.get("obstacles") or []
    obstacles = set(tuple(p) for p in obs_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(x, a, b):
        if x < a:
            return a
        if x > b:
            return b
        return x

    # Precompute resources sorted deterministically for tie-breaking
    resources = sorted((int(x), int(y)) for x, y in res)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            # engine would keep us in place; evaluate that instead
            nx, ny = sx, sy

        # If we can collect now, take it deterministically
        if (nx, ny) in set(resources):
            key = (10**9, nx, ny)
            if best_score is None or key > best_score:
                best_score = key
                best_move = (dx, dy)
            continue

        # Otherwise, pick the resource that maximizes advantage at this next position
        # advantage = (opp_dist - self_dist), then prefer closer self distance, then lexicographic resource
        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            key = (adv, -ds, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key
        if local_best is None:
            key = (-10**9, 0, 0)
        else:
            adv, nds, nrx, nry = local_best
            # Slightly penalize moving away from center to reduce dithering
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            dist_center = abs(nx - cx) + abs(ny - cy)
            key = (adv, nds, -dist_center, -nx, -ny)

        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]