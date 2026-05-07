def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set(map(tuple, obs_list))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def steps(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diag allowed

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    def cell_penalty(x, y):
        # Strongly avoid standing on/next to obstacles (if engine rejects, staying is safe anyway)
        p = 0.0
        if (x, y) in obstacles:
            p -= 1000000.0
        for ax, ay in obs_list:
            if max(abs(ax - x), abs(ay - y)) == 0:
                p -= 1000000.0
            elif max(abs(ax - x), abs(ay - y)) == 1:
                p -= 30.0
        return p

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            nx, ny = sx, sy  # engine would keep in place; mirror deterministically
        base = cell_penalty(nx, ny)

        # Evaluate best resource for this candidate; deterministic tie-break by closer-to-opponent distance
        best_val = -10**18
        for rx, ry in resources:
            ds = steps((nx, ny), (rx, ry))
            do = steps((ox, oy), (rx, ry))

            # Prefer earlier arrival; if not earlier, still deny by maximizing (opponent-self) margin
            if ds < do:
                val = (1000000 - ds) + (do - ds)  # big preference for taking first
            else:
                val = (do - ds) - ds  # deny and don't fall too far behind

            # Slight preference for reduced remaining distance to our chosen target
            val += -0.01 * (abs(rx - nx) + abs(ry - ny))
            if val > best_val or (val == best_val and do < steps((ox, oy), (rx, ry))):
                best_val = val

        total = base + best_val
        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]