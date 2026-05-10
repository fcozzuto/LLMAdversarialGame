def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obs

    def dist2(x, y, a, b):
        dx = x - a
        dy = y - b
        return dx * dx + dy * dy

    def cheb(x, y, a, b):
        dx = x - a
        if dx < 0:
            dx = -dx
        dy = y - b
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    role = (observation.get("self_role") or "").lower()
    pursue = role != "evader"

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    # Opposite-corner target: try to force opponent into the corner farthest from their current location
    tx, ty = max(corners, key=lambda c: dist2(ox, oy, c[0], c[1]))

    # Deterministic move ordering (no randomness)
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_score = None
    best_tiebreak = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        d_opp = dist2(nx, ny, ox, oy)
        d_goal = dist2(nx, ny, tx, ty)

        # Obstacle proximity penalty to avoid getting stuck near walls
        adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (px, py) in obs:
                    adj += 1

        # Greedy intercept: prioritize opponent distance (capture), then push toward opposite corner
        # Evader: reverse preferences
        score = (d_opp * (1.0 if pursue else -1.0)) + (0.25 * d_goal * (1.0 if pursue else -1.0)) + (0.15 * adj)

        # Tie-break deterministically: maximize progress along Chebyshev to target (or away if evader)
        progress = cheb(nx, ny, ox, oy)
        prog_key = (-progress if pursue else progress)

        tiebreak = (prog_key, -d_goal, -abs(dx), -abs(dy))
        if best_score is None:
            best_score = score
            best_tiebreak = tiebreak
            best_move = [dx, dy]
        else:
            better = score < best_score if pursue else score > best_score
            if better or (score == best_score and tiebreak > best_tiebreak):
                best_score = score
                best_tiebreak = tiebreak
                best_move = [dx, dy]

    return best_move if ok(sx + best_move[0], sy + best_move[1]) else [0, 0]