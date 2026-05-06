def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    if not resources:
        return [0, 0]
    obs = {(p[0], p[1]) for p in obstacles}

    def dist(x1, y1, x2, y2):
        return abs(x2 - x1) + abs(y2 - y1)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            nx, ny = sx, sy
        self_best = -10**18
        for rx, ry in resources:
            myd = dist(nx, ny, rx, ry)
            opd = dist(ox, oy, rx, ry)
            # Core: prioritize resources where we're closer than opponent
            val = opd - myd
            # If opponent is extremely close to that resource, avoid over-committing
            if opd <= 1:
                val -= 3.5 + 0.6 * myd
            # If opponent can beat us to it quickly, devalue
            if opd - myd >= 1:
                val -= 0.35 * (opd - myd)
            # Small tie-break: prefer nearer completion
            val += 0.02 * (10 - myd)
            # Deterministic resource tie-break by coordinates
            val += rx * 1e-4 + ry * 1e-6
            if val > self_best:
                self_best = val
        # Add gentle pressure to move closer to opponent to enable interception/delay
        self_best += 0.01 * (dist(nx, ny, ox, oy) * -1)
        if self_best > best_val:
            best_val = self_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]