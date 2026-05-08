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
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def cheb(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        return dx if dx >= 0 else -dx if -dx >= 0 else -dx

    def cheb2(x, y, x2, y2):
        dx = x - x2
        dy = y - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def dist2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    # Select a meaningful strategic corner target depending on role.
    if pursuer:
        # Move toward the corner that is closer to the opponent (helps net corner pressure).
        target = min(corners, key=lambda c: dist2(c[0], c[1], ox, oy))
    else:
        # Move toward the corner farthest from the opponent.
        target = max(corners, key=lambda c: dist2(c[0], c[1], ox, oy))

    best_score = None
    best_move = [0, 0]

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny, dx, dy = sx, sy, 0, 0

        d = cheb2(nx, ny, ox, oy)
        tc = cheb2(nx, ny, target[0], target[1])
        # Small obstacle-aware term: prefer staying with more free neighboring cells.
        free_n = 0
        for adx, ady in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            px, py = nx + adx, ny + ady
            if 0 <= px < w and 0 <= py < h and (px, py) not in obs:
                free_n += 1

        # Deterministic scalar objective.
        if pursuer:
            score = (-d * 100.0) + (-tc * 1.0) + (free_n * 0.25) + (-dist2(nx, ny, target[0], target[1]) * 0.0005)
        else:
            score = (d * 100.0) + (-tc * 1.0) + (free_n * 0.25) + (-dist2(nx, ny, target[0], target[1]) * 0.0005)

        # Deterministic tie-break: lexicographic by move.
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    return best_move