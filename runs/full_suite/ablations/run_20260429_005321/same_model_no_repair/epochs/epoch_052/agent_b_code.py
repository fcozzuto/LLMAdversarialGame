def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    res = observation.get("resources", [])
    if not res:
        return [0, 0]

    blocked = set((x, y) for x, y in obstacles)

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(x, y):
        return 0 <= x < observation["grid_width"] and 0 <= y < observation["grid_height"]

    def score_target(px, py, tx, ty):
        ds = abs(tx - px) + abs(ty - py)
        do = abs(tx - ox) + abs(ty - oy)
        # prefer targets we can reach meaningfully sooner than opponent
        return (do - ds) * 4 - ds

    best_move = (0, 0)
    best_val = -10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in blocked:
                continue

            # Immediate target selection based on current reachable advantage
            # (dominant deterministic choice, no randomness).
            local_best = -10**9
            for tx, ty in res:
                if (tx, ty) in blocked:
                    continue
                local_best = max(local_best, score_target(nx, ny, tx, ty))

            # Obstacle pressure: discourage moves that bring us "into" obstacle adjacency.
            adj_pen = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    if ax == 0 and ay == 0:
                        continue
                    if (nx + ax, ny + ay) in blocked:
                        adj_pen += 2

            val = local_best - adj_pen
            if val > best_val:
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]