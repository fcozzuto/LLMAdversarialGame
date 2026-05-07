def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
    if not moves:
        return [0, 0]

    res_set = set((p[0], p[1]) for p in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    if not resources:
        targets = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bx, by = max(targets, key=lambda c: (-(abs(c[0] - sx) + abs(c[1] - sy)) + (abs(c[0] - ox) + abs(c[1] - oy)) * 0.5))
        dx = 0 if bx == sx else (1 if bx > sx else -1)
        dy = 0 if by == sy else (1 if by > sy else -1)
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in obstacles or not inb(nx, ny):
            return [0, 0]
        return [dx, dy]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        self_pos = (nx, ny)

        # Evaluate best resource race advantage for this step.
        # Prefer cells where you can reach a resource at least as fast as the opponent.
        value = -10**9
        for r in resources:
            rx, ry = r[0], r[1]
            self_d = abs(rx - nx) + abs(ry - ny)
            opp_d = abs(rx - ox) + abs(ry - oy)
            # If opponent is closer, penalize strongly; if tie/you closer, reward sharply.
            advantage = (opp_d - self_d)
            value = max(value, advantage * 100 - self_d * 2 + (1 if (nx, ny) == (rx, ry) else 0) * 50)

        # Secondary tie-break: avoid getting too close to opponent unless it helps race a resource.
        opp_prox = -man(self_pos, (ox, oy))
        value = value + opp_prox * 0.2

        if best_val is None or value > best_val:
            best_val = value
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]