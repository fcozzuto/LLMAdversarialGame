def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    if not resources:
        return [0, 0]

    obs_set = set((x, y) for x, y in obstacles)

    def cheb(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    best_self_dist = 10**9

    opp = (ox, oy)

    for dx, dy in moves:
        nx = sx + dx
        ny = sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue

        selfp = (nx, ny)
        self_to_best = 10**9
        gain = -10**18

        for r in resources:
            sd = cheb(selfp, r)
            od = cheb(opp, r)
            self_to_best = sd if sd < self_to_best else self_to_best
            g = od - sd
            if g > gain:
                gain = g

        # Prefer moves that win resource proximity; small tie-break for closeness to nearest resource.
        score = gain * 1000 - self_to_best
        if score > best_score or (score == best_score and self_to_best < best_self_dist):
            best_score = score
            best_self_dist = self_to_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]