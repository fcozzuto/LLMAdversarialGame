def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    def clamp(x, y):
        if x < 0: x = 0
        if x >= w: x = w - 1
        if y < 0: y = 0
        if y >= h: y = h - 1
        return x, y

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_action(px, py):
        if not resources:
            return (-md(px, py, ox, oy), 0, 0)
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = md(px, py, rx, ry)
            do = md(ox, oy, rx, ry)
            dist_term = -ds * 1.2
            opp_term = (do - ds) * 1.8  # prefer resources where we are closer than opponent
            closeness = -(ds) * 0.3
            val = dist_term + opp_term + closeness
            if best is None or val > best[0]:
                best = (val, rx, ry)
        return best

    best_move = (None, -10**9)
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            continue
        val, rx, ry = best_action(nx, ny)
        # If move reaches the chosen resource, boost strongly.
        reach = 30 if (nx == rx and ny == ry) else 0
        # Avoid letting opponent cut off: prefer increasing distance from opponent.
        opp_dist = md(nx, ny, ox, oy)
        opp_term = opp_dist * 0.15
        total = val + reach + opp_term
        if total > best_move[1]:
            best_move = ((dx, dy), total)

    if best_move[0] is None:
        return [0, 0]
    dx, dy = best_move[0]
    return [dx, dy]