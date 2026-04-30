def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obs_set = set((p[0], p[1]) for p in obstacles)
    res_list = [(p[0], p[1]) for p in resources]

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                moves.append((dx, dy, nx, ny))

    if not res_list:
        return [0, 0]

    # If opponent is extremely close to a resource, prioritize a different one.
    best_move = None
    best_score = -10**18
    for dx, dy, nx, ny in moves:
        # Base: prefer increasing advantage to a resource.
        # Advantage is (opponent distance - our distance): larger means we are closer.
        # Add small term for moving toward the globally best resource.
        score = 0
        my_pos = (nx, ny)
        for rx, ry in res_list:
            our_d = dist2(my_pos, (rx, ry))
            opp_d = dist2((ox, oy), (rx, ry))
            # Prefer resources we can beat opponent on.
            adv = opp_d - our_d
            score += adv

            # Mild penalty if we would be moving into the opponent's immediate vicinity.
            if dist2(my_pos, (ox, oy)) <= 2:
                score -= 5

        # Obstacle/edge pressure: slight preference for central-ish and safer tiles.
        edge_pen = (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.01
        score -= edge_pen

        # If opponent can reach many resources faster, try to reduce their lead sharply.
        lead_loss = 0
        for rx, ry in res_list:
            our_now = dist2((sx, sy), (rx, ry))
            our_new = dist2((nx, ny), (rx, ry))
            opp_d = dist2((ox, oy), (rx, ry))
            # Only reward improvements that reduce our distance relative to opponent.
            if our_new < our_now:
                lead_loss += max(0, (opp_d - our_new) - (opp_d - our_now)) * 0.1
        score += lead_loss

        # Deterministic tie-break: prefer smaller dx then smaller dy then staying.
        tie = (dx, dy)
        total = (score, -abs(dx) - abs(dy), - (0 if dx == 0 and dy == 0 else 1), -tie[0], -tie[1])
        if best_move is None or total > best_score:
            best_score = total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]