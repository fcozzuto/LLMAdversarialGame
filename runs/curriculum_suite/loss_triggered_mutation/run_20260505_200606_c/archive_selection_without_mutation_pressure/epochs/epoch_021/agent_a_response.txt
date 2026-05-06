def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best_dx, best_dy = 0, 0
    best_score = -10**18

    # Identify the most "contestable" resource: where we can become closer than the opponent.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0
        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)
            advantage = opp_d - our_d  # positive is good

            # Row-alignment bias: edge_patrol tends to sweep; aligning y reduces their effective chase.
            row_gap = abs(ny - ry)
            row_bonus = 6 - row_gap * 2
            if row_bonus < 0:
                row_bonus = 0

            # Prefer resources that are not too far behind opponent.
            contest_bonus = 0
            if advantage >= 0:
                contest_bonus = 8 + advantage * 2
            else:
                contest_bonus = -min(10, (-advantage))

            # Small blocking term: reduce distance to opponent when contesting.
            block_term = 0
            if advantage >= 0:
                block_term = (man(nx, ny, rx, ry) - man(ox, oy, rx, ry)) * 0  # keep deterministic but neutral

            score += row_bonus + contest_bonus + advantage * 1.5 + block_term

        # Mild preference for moves that keep options open (avoid stepping into tight corners).
        centerish = (nx - (w - 1) / 2) ** 2 + (ny - (h - 1) / 2) ** 2
        score -= centerish * 0.01

        if score > best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]