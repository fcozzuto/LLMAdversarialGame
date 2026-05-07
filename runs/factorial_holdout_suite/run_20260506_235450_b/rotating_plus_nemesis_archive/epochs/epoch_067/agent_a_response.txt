def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obs = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def neighbor_obstacle_penalty(x, y):
        p = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    p += 1
        return p

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    best_move = (0, 0)
    best_val = -10**18

    # Evaluate moves by choosing the best target under a "race" heuristic
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        step_pen = neighbor_obstacle_penalty(nx, ny)
        # choose best target reachable (heuristic only), then score this move
        move_best = -10**18
        for tx, ty in resources:
            self_d = dist((nx, ny), (tx, ty))
            opp_d = dist((ox, oy), (tx, ty))
            # prioritize winning the race; tie-break with lower self distance
            race = opp_d - self_d
            val = race * 100 - self_d - step_pen * 2
            if val > move_best:
                move_best = val
        # small bias to reduce distance to current best target direction
        if move_best > best_val or (move_best == best_val and (dx, dy) == (0, 0) is False):
            best_val = move_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]