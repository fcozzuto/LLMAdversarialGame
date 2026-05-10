def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))

    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_t = set(map(tuple, observation.get("self_territory") or []))
    opp_t = set(map(tuple, observation.get("opponent_territory") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dist_to_opp = abs(sx - ox) + abs(sy - oy)

    dirs = [(0, 0), (-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            nx, ny, dx, dy = sx, sy, 0, 0

        score = 0.0

        if (nx, ny) in opp_t:
            score += 45.0
        elif (nx, ny) in unclaimed:
            score += 14.0
        elif (nx, ny) in self_t:
            score += 4.0

        # Intercept opponent: prefer reducing distance to opponent.
        new_dist_opp = abs(nx - ox) + abs(ny - oy)
        score += (dist_to_opp - new_dist_opp) * 3.5

        # Control the center to deny edge-based spread.
        score += -0.9 * (abs(nx - cx) + abs(ny - cy))

        # Cut off: if move is near opponent territory, prioritize it.
        if opp_t:
            near = min(abs(nx - px) + abs(ny - py) for (px, py) in opp_t)
            score += max(0.0, 6.0 - 0.9 * near)

        # Slightly discourage giving opponent immediate access.
        if (nx, ny) in unclaimed:
            score -= 0.8 * min(abs(ox - px) + abs(oy - py) for (px, py) in unclaimed or [(ox, oy)])

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move