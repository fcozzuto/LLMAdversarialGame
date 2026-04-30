def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal_from(x, y):
        out = []
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        return out

    lm_self = legal_from(sx, sy)
    if not lm_self:
        return [0, 0]

    # If no resources, head to center, while keeping away from obstacles.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in lm_self:
            d = cheb(nx, ny, tx, ty)
            # obstacle proximity penalty
            prox = 0
            for ax, ay in obstacles:
                prox = max(prox, 3 - cheb(nx, ny, ax, ay))
            key = (d, -prox, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    # Precompute resource distances from opponent for tie/intercept logic.
    opp_d = []
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        opp_d.append((cheb(ox, oy, rx, ry), rx, ry))

    # Main heuristic:
    # - prioritize taking a resource we can reach at least as fast as opponent
    # - otherwise prioritize minimizing our distance to the closest resource
    # - add a small "block" term: prefer next positions that increase opponent distance advantage.
    best = None
    for dx, dy, nx, ny in lm_self:
        our_best = 10**9
        intercept_gain = -10**9
        closest_r = None
        for od, rx, ry in opp_d:
            d = cheb(nx, ny, rx, ry)
            if d < our_best:
                our_best = d
                closest_r = (rx, ry)
            gain = od - d  # positive means we are closer/faster than opponent
            if gain > intercept_gain:
                intercept_gain = gain

        # Small obstacle-avoidance: discourage moving toward immediate obstacle neighborhood.
        obs_pen = 0
        for ax, ay in obstacles:
            dist = cheb(nx, ny, ax, ay)
            if dist <= 1:
                obs_pen = max(obs_pen, 3 - dist)

        # If we can directly grab a resource (gain big), heavily favor it.
        # Otherwise, minimize our distance to the closest resource, then maximize intercept_gain.
        if intercept_gain >= 1:
            key = (-intercept_gain, our_best, obs_pen, dx, dy)
        else:
            key = (our_best, -intercept_gain, obs_pen, dx, dy)

        if best is None or key < best[0]:
            best = (key, (dx, dy))

    return [best[1][0], best[1][1]]