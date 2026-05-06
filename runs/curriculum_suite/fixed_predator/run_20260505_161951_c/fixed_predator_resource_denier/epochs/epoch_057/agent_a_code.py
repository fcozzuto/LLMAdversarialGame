def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Terminal / no resources: maximize distance from opponent while heading to farthest corner from opponent
    if not resources:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
        best = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy) * 1000 - (abs(nx - tx) + abs(ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick move that maximizes advantage on the most important contested resource.
    # Advantage: (opponent_distance - self_distance) with extra push to reduce our distance for the best target,
    # and to increase opponent distance for cells they are likely to take.
    best = (0, 0)
    bestv = -10**18
    opp_corner_bias = (w - 1 - ox) * (h - 1 - oy)  # deterministic mild bias
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        self_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we're behind, we want to close; if ahead, we want to keep.
            advantage = (do - ds)
            # Denial pressure: favor cells where opponent is close but we can meaningfully reduce distance.
            v = advantage * 200 - ds - max(0, do - ds) * 3
            # Secondary: slight preference for cells closer to our move direction corner to break ties deterministically
            v += (rx * 13 + ry * 7 + opp_corner_bias) % 5
            if v > self_best:
                self_best = v
        if self_best > bestv or (self_best == bestv and (dx, dy) < best):
            bestv = self_best
            best = (dx, dy)
    return [best[0], best[1]]