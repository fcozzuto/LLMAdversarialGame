def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = set(map(tuple, obstacles)) if obstacles else set()

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

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

    def nearest_dist(x, y):
        d = None
        for rx, ry in resources:
            t = cheb(x, y, rx, ry)
            if d is None or t < d:
                d = t
        return d

    def best_resource_score(x, y):
        # Encourage moving to areas with multiple nearby resources (greedy density)
        if not resources:
            return None
        r = 2  # small neighborhood
        cnt = 0
        bestd = 10**9
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if d <= r:
                cnt += 1
            if d < bestd:
                bestd = d
        if bestd == 10**9:
            bestd = None
        return cnt, bestd

    if not resources:
        # Fall back to approaching opponent to force contest (still deterministic)
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    my_opp = nearest_dist(ox, oy)
    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs_set:
            continue
        my_d = nearest_dist(nx, ny)
        if my_d is None:
            continue
        cnt, bestd = best_resource_score(nx, ny)
        # Core: beat opponent by getting closer; tie-break: prefer earlier/denser resource clusters
        val = (my_opp - my_d) + 0.25 * cnt - 0.01 * cheb(nx, ny, ox, oy)
        # If at same distance, prefer actions that reduce distance to the closest resource
        if bestd is not None:
            val += 0.02 * (my_d == bestd)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move