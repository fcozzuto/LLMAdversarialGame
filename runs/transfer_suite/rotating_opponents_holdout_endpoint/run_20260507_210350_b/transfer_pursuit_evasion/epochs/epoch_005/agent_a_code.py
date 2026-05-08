def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs_list = observation.get("obstacles", [])
    obs = set((x, y) for x, y in obs_list)

    role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    pursuer = ("pursuer" in role) or ("evader" in opp_role)

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Target corner heuristic
    if pursuer:
        target = min(corners, key=lambda c: cheb(c[0], c[1], ox, oy))
    else:
        target = max(corners, key=lambda c: cheb(c[0], c[1], ox, oy))

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        d_opp = cheb(nx, ny, ox, oy)
        d_corner = cheb(nx, ny, target[0], target[1])
        # Also discourage getting closer to the "opponent escape axis" when evading
        d_corner_opp = cheb(ox, oy, target[0], target[1])

        if pursuer:
            score = (-d_opp * 100) - d_corner - (0 if d_corner_opp == d_corner_opp else 0)
        else:
            score = (d_opp * 100) - d_corner + (0.5 * (d_corner_opp))
        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
    return best