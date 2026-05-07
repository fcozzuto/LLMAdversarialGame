def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}
    resources = observation.get("resources", []) or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx + dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            for rx, ry in resources:
                if nx == rx and ny == ry:
                    return [dx, dy]

    if not resources:
        return [0, 0]

    best = [0, 0]
    best_key = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        min_self = 10**9
        min_opp = 10**9
        nearest = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            if ds < min_self:
                min_self = ds
                nearest = (rx, ry)
            if do < min_opp:
                min_opp = do

        # Advantage to win the next contested resource (approx: compare current opponent distance)
        # Encourage moving toward the specific resource that is currently closest to us.
        rx, ry = nearest
        my_d = md(nx, ny, rx, ry)
        opp_d = md(ox, oy, rx, ry)
        advantage = opp_d - my_d

        # Mild penalty for getting too close to any obstacle (robustness)
        obs_pen = 0
        for ax, ay in ((nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1), (nx - 1, ny - 1), (nx + 1, ny + 1), (nx - 1, ny + 1), (nx + 1, ny - 1)):
            if 0 <= ax < w and 0 <= ay < h and (ax, ay) in obstacles:
                obs_pen += 1

        # Prefer smaller my_d after maximizing advantage; deterministic tie-break by move ordering already fixed.
        key = (-(advantage), my_d, obs_pen, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best