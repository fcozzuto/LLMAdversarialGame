def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(map(tuple, observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def steps(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diag allowed

    # If no resources, drift toward center (still deterministic)
    if not resources:
        cx, cy = w // 2, h // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def best_value(px, py):
        best = (-10**9, None)
        for rx, ry in resources:
            ds = steps((px, py), (rx, ry))
            do = steps((ox, oy), (rx, ry))
            # Prefer being earlier; if not, deny by maximizing the gap (opponent - self).
            if ds < do:
                val = (1000000 - ds) + (do - ds)  # strongly favor earlier arrival
            else:
                val = (do - ds) - ds  # deny / at least not fall too far behind
            # Slightly prefer closer to our position to reduce dithering
            val = val + (-0.001 * (abs(rx - px) + abs(ry - py)))
            if val > best[0]:
                best = (val, (rx, ry))
        return best[0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        val = best_value(nx, ny)
        # Tie-break: prefer moves that reduce distance to opponent-advantage resources
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]