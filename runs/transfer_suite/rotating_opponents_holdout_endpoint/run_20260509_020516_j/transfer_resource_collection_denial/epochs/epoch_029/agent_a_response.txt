def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", None) or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", None) or []:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # Prefer staying aligned toward opponent to reduce escape.
        dx = 0 if ox == sx else (1 if ox > sx else -1)
        dy = 0 if oy == sy else (1 if oy > sy else -1)
        return [dx, dy]

    # Score targets by who gets there first (tie-breaker favors being closer/earlier).
    # Favor moves that maximize lead; break ties by minimizing own distance.
    def target_value(px, py, tx, ty):
        self_d = md((px, py), (tx, ty))
        opp_d = md((ox, oy), (tx, ty))
        # Lead dominates; own speed breaks ties.
        return (opp_d - self_d) * 1000 - self_d

    best = None
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        val = -nx * 0  # keep deterministic/no extra randomness
        # If move is onto a resource, heavily reward.
        if (nx, ny) in resources:
            val += 10**9

        # Main: choose best target reachable from this next position.
        local_best = -10**18
        for tx, ty in resources:
            local_best = max(local_best, target_value(nx, ny, tx, ty))

        # Secondary: slight preference to move away from obstacles by maximizing free neighborhood.
        # (Helps avoid getting trapped behind the fixed obstacle layout.)
        free = 0
        for adx, ady in moves:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) not in obstacles:
                free += 1

        val += local_best + free * 2 - (abs(nx - ox) + abs(ny - oy)) * 0.01

        if val > best_val:
            best_val = val
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]