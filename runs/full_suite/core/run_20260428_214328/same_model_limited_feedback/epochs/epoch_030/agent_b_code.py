def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"] or []
    obstacles = set(tuple(p) for p in (observation["obstacles"] or []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = w // 2, h // 2
        if (sx, sy) == (ox, oy):
            tx, ty = ox, oy
        best = None
        bestv = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            v = -((nx - tx) ** 2 + (ny - ty) ** 2)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best if best is not None else (0, 0))
    # Choose a move that improves access to resources while being harder for opponent to reach.
    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    resset = set(tuple(p) for p in resources)
    k = 0.85  # emphasize distancing opponent
    bonus = 1e6
    best = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        movev = 0.0
        if (nx, ny) in resset:
            movev += bonus
        # pick best reachable resource target for this candidate
        best_target_v = -10**18
        for rx, ry in resources:
            ds = dist2(nx, ny, rx, ry)
            do = dist2(ox, oy, rx, ry)
            # Prefer small ds and large do; also prefer closer resources generally.
            tv = -ds + k * do - 0.002 * (ds + do)
            if (rx, ry) == (nx, ny):
                tv += bonus * 0.1
            if tv > best_target_v:
                best_target_v = tv
        movev += best_target_v
        # Slightly discourage moving into immediate proximity of obstacles (soft safety)
        for ax, ay in obstacles:
            if abs(nx - ax) <= 1 and abs(ny - ay) <= 1:
                movev -= 50.0
        # If tie, prefer not to stay (meaningful change)
        if movev > bestv + 1e-9 or (abs(movev - bestv) <= 1e-9 and (dx, dy) != (0, 0) and (best == (0, 0))):
            bestv = movev
            best = (dx, dy)
    return [best[0], best[1]]