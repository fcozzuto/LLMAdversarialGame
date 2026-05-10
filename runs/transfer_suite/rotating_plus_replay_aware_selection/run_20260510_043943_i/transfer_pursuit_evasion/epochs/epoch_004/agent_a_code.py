def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursuer" in self_role) or ("chaser" in self_role) or ("hunter" in self_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2; dy = y1 - y2
        return dx * dx + dy * dy

    def obstacle_density(x, y):
        r = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs:
                    r += 1
        return r

    def free_neighbors(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                c += 1
        return c

    # Deterministic tie-break: prefer smaller (dx,dy) lexicographically
    best_move = None
    best_score = None

    # Corner bias to keep deterministic "directional" play when distances tie
    corner_targets = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    # Choose a target based on relative position to opponent (deterministic)
    # For pursuer: bias toward opponent's corner relative direction; for evader: bias away.
    if abs(ox - (w - 1)) + abs(oy - (h - 1)) <= abs(ox - 0) + abs(oy - (h - 1)):
        corner = (w - 1, h - 1) if (ox + oy) % 2 == 0 else (0, h - 1)
    else:
        corner = (0, 0) if (ox + oy) % 2 == 0 else (w - 1, 0)

    for dx, dy, nx, ny in valid:
        d = dist2(nx, ny, ox, oy)
        dens = obstacle_density(nx, ny)
        fn = free_neighbors(nx, ny)

        if is_pursuer:
            # primary: minimize distance to opponent
            # secondary: avoid clutter / dead-ends
            score = (-d) - 1.2 * dens + 0.6 * fn
            # additional: steer roughly toward opponent's current cell by corner bias if still tied
            score += -0.03 * dist2(nx, ny, corner[0], corner[1])
        else:
            # primary: maximize distance to pursuer
            # secondary: avoid clutter; prefer positions with more freedom
            score = (d) - 1.2 * dens + 0.6 * fn
            # additional: bias toward the farthest corner to prolong survival
            score += 0.03 * dist2(nx, ny, corner[0], corner[1])

        key = (score, -dx, -dy)  # helps deterministic ordering when floating; no randomness
        if best_score is None or key > best_score:
            best_score = key
            best_move = [dx, dy]

    return best_move