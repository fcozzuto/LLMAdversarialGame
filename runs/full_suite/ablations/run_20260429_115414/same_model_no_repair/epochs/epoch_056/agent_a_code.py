def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def obs_adj(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    c += 1
        return c

    best_move = [0, 0]
    best_val = -10**18

    # Pick move that maximizes advantage toward some resource, while avoiding obstacles.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_adj = obs_adj(nx, ny)
        base = -2 * my_adj

        # Anticipate contention: favor resources where we get closer than opponent.
        best_res_val = -10**18
        for rx, ry in resources:
            myd = manh(nx, ny, rx, ry)
            opd = manh(ox, oy, rx, ry)
            # Positive when we are closer.
            adv = (opd - myd)
            # Strongly prefer immediate capture next turn.
            cap = 8 if myd == 0 else (4 if myd == 1 else 0)
            # Slightly avoid very hard targets.
            hard_pen = -0.3 * myd
            # Deny resources that opponent is about to reach.
            deny = 6 if opd == 1 and myd > 1 else (2 if opd == 1 and myd == 1 else 0)
            val = 5 * adv + cap + hard_pen + deny
            # Deterministic tie-break by coordinates.
            val += -0.001 * (rx * 9 + ry)
            if val > best_res_val:
                best_res_val = val
        total = base + best_res_val

        if total > best_val:
            best_val = total
            best_move = [dx, dy]

    return best_move