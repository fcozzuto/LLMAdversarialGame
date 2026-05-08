def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_pos = observation.get("self_position", [0, 0])
    opp_pos = observation.get("opponent_position", [0, 0])
    self_role = (observation.get("self_role", "") or "").lower()
    obstacles = observation.get("obstacles", []) or []
    ox = {tuple(p) for p in obstacles}
    sx, sy = int(self_pos[0]), int(self_pos[1])
    px, py = int(opp_pos[0]), int(opp_pos[1])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))
    # Prefer not staying if equally good
    moves.sort(key=lambda t: (0 if t != (0, 0) else 1, t[0], t[1]))

    def dist(a, b):
        # Chebyshev distance matches diagonal movement
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    is_pursuer = ("purs" in self_role) or ("chase" in self_role)
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        nx, ny = clamp(nx, 0, w - 1), clamp(ny, 0, h - 1)
        if (nx, ny) in ox:
            continue

        # If we can capture (pursuer), take it immediately
        if is_pursuer and (nx, ny) == (px, py):
            return [dx, dy]

        # If opponent is pursuer, avoid being captured
        if (not is_pursuer) and (nx, ny) == (px, py):
            continue

        # Score from perspective of maximizing final intent
        d = dist((nx, ny), (px, py))
        # For pursuer: minimize distance; for evader: maximize distance
        # Add obstacle-aware small term by penalizing proximity to obstacles
        obs_pen = 0
        for (oxx, oyy) in ox:
            t = max(abs(nx - oxx), abs(ny - oyy))
            if t == 0:
                obs_pen += 1000
            elif t == 1:
                obs_pen += 3
            elif t == 2:
                obs_pen += 1

        # Tie-break toward center for pursuer, toward corner for evader (deterministic bias)
        center = (w - 1) / 2.0, (h - 1) / 2.0
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        center_bias = dist((nx, ny), (int(center[0]), int(center[1])))
        corner_bias = max(dist((nx, ny), c) for c in corners)

        if is_pursuer:
            score = (-d * 100) - obs_pen - center_bias
        else:
            score = (d * 100) - obs_pen + corner_bias

        if best is None or score > best_score:
            best = (dx, dy)
            best_score = score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]