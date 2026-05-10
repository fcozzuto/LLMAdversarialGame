def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    sx, sy = self_pos[0], self_pos[1]
    ox, oy = opp_pos[0], opp_pos[1]
    obstacles = observation.get("obstacles", [])
    obs = set((p[0], p[1]) for p in obstacles)

    self_role = observation.get("self_role", "")
    is_pursuer = ("pursuer" in self_role.lower()) or ("chaser" in self_role.lower())

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            valid.append((dx, dy, nx, ny))

    if not valid:
        return [0, 0]

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    if is_pursuer:
        # Greedy chase: minimize squared distance, with tie-break toward exact capture then toward lower dx/dy lexicographically
        for dx, dy, nx, ny in valid:
            d = dist2(nx, ny, ox, oy)
            cap = 1 if (nx == ox and ny == oy) else 0
            key = (-cap, d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
    else:
        # Evade: maximize squared distance from pursuer; prefer not moving closer, avoid obstacles already handled
        for dx, dy, nx, ny in valid:
            d = dist2(nx, ny, ox, oy)
            # slight preference for moving away in x/y components deterministically
            away_score = (1 if (nx - ox) * (sx - ox) >= 0 else 0) + (1 if (ny - oy) * (sy - oy) >= 0 else 0)
            key = (-away_score, -d, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))

    return [int(best[1][0]), int(best[1][1])]