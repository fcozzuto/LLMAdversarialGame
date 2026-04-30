def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set((p[0], p[1]) for p in obstacles)

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18
    best_adv = -10**18
    cx = (w - 1) // 2
    cy = (h - 1) // 2

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obs:
            continue

        our_best_adv = -10**18
        our_best_dist = 10**18
        center_dist = cheb(nx, ny, cx, cy)

        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            adv = opp_d - our_d  # larger => we are closer

            if adv > our_best_adv or (adv == our_best_adv and our_d < our_best_dist):
                our_best_adv = adv
                our_best_dist = our_d

        # Primary: maximize advantage over opponent for the best contested resource
        # Secondary: get that resource sooner
        # Tertiary: drift toward center to keep flexibility
        score = our_best_adv * 1000 - our_best_dist - center_dist
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]