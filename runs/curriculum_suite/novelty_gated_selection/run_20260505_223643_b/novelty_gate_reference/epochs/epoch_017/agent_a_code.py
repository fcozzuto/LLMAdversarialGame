def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles}

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # If on resource, stay
    for r in resources:
        if int(r[0]) == sx and int(r[1]) == sy:
            return [0, 0]

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None  # (score, -self_d, dx, dy)

    # Heuristic: maximize (opp_best_dist - self_best_dist) after move; tie-break closer to a resource and away from obstacles.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        self_best = 10**9
        opp_best = 10**9
        # Also keep second-order: avoid getting stuck near obstacles
        near_obs = 0
        for (px, py) in [(nx-1, ny), (nx+1, ny), (nx, ny-1), (nx, ny+1), (nx-1, ny-1), (nx+1, ny+1), (nx-1, ny+1), (nx+1, ny-1)]:
            if (px, py) in obs:
                near_obs += 1

        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if sd < self_best: self_best = sd
            if od < opp_best: opp_best = od

        adv = opp_best - self_best  # higher is better
        # If cannot beat opponent on nearest resource, still prefer shorter self_best, but discourage being too close to obstacle clusters.
        score = adv * 100 - self_best - near_obs * 0.5

        cand = (score, -self_best, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]