def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    obs = {(x, y) for x, y in obstacles}

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role) or ("evader" in opp_role)
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    # Bias to reduce (pursuer) / increase (evader) Chebyshev distance, robust to diagonal play.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        d2 = dist2(nx, ny, ox, oy)
        cheb = max(abs(nx - ox), abs(ny - oy))

        # Encourage moving in the general direction toward/away from opponent.
        dirx = 0 if ox == nx else (1 if ox > nx else -1)
        diry = 0 if oy == ny else (1 if oy > ny else -1)
        align = (dx != 0 and dx == dirx) + (dy != 0 and dy == diry) + (dx == 0 and dirx == 0) + (dy == 0 and diry == 0)

        # Small center-bias to avoid corner stagnation when distances tie.
        center = -((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        # Objective: pursuer -> maximize (-cheb, -d2); evader -> maximize (cheb, d2)
        if pursuer:
            val = (-cheb) * 1000 + (-d2) + 3 * align + 0.01 * center
        else:
            val = (cheb) * 1000 + (d2) + 3 * align + 0.01 * center

        if best is None or val > best:
            best = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]