def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Greedy contest value: prefer resources where we are closer than opponent, and especially immediate pickups.
        val = None
        for rx, ry in resources:
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)

            # Immediate pickup (strongly prefer).
            pickup_bonus = 500 if (nx == rx and ny == ry) else 0

            # If we can get there sooner than opponent, boost; otherwise penalize.
            contest = (do - ds)

            # Mild bias: move in direction that reduces our average remaining y-distance to resources.
            # (Deterministic and helps break ties against deniers.)
            y_bias = -abs(ry - ny) + -abs(ry - oy) * 0.15

            cur = pickup_bonus + contest * 30 + y_bias

            if val is None or cur > val:
                val = cur

        if val is None:
            continue
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]