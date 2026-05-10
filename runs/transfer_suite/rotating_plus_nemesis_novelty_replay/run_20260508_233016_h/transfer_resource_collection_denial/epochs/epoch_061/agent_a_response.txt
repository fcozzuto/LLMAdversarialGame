def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy  # Chebyshev

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Choose a target resource by maximizing our "eventual control" over it.
    # If we can't secure any, pick the one that minimizes opponent advantage.
    best = None
    for rx, ry in resources:
        dm = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        # Prefer secure, then prefer smallest time-to-go for us, then biggest gap.
        secure = dm < do
        key = (
            0 if secure else 1,
            dm if secure else dm - do,  # secure: earlier is better; contested: more negative is better
            -(do - dm),  # larger gap for secure
            rx, ry
        )
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    # Move evaluation: advance toward target, keep away from obstacles, and reduce opponent's access.
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0),  (0, 0),  (1, 0),
              (-1, 1),  (0, 1),  (1, 1)]
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        my_d = dist(nx, ny, tx, ty)
        op_d = dist(ox, oy, tx, ty)

        # If we reduce the distance enough to be strictly ahead, boost.
        dm_now = dist(sx, sy, tx, ty)
        ahead_now = dm_now < op_d
        ahead_next = my_d < op_d

        # Obstacle proximity penalty (discourages cornering).
        near_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                cx, cy = nx + ax, ny + ay
                if inb(cx, cy) and (cx, cy) in obstacles:
                    near_obs += 1

        # Small tie-break to avoid oscillation: prefer moves that also move away from opponent when losing.
        lose = (dist(sx, sy, tx, ty) >= dist(ox, oy, tx, ty))
        away = dist(nx, ny, ox, oy) if lose else 0

        val = (
            0 if ahead_next else 1,
            my_d if ahead_next else my_d + 2 * max(0, my_d - op_d),
            -away,
            near_obs,
            abs(nx - tx) + abs(ny - ty),
            rx if False else 0  # deterministic no-op placeholder avoided by fixed 0
        )

        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move