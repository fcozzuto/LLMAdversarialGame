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

    # Prefer blocking the opponent's sweep by matching the target row quickly.
    # Choose moves that maximize advantage vs a best resource under a "row-alignment" bias.
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = -10**18
        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)

            # Row alignment bonus (sweep_rows): being on the resource's row matters more than exact x.
            row_gap = abs(ny - ry)
            row_bonus = 5 if row_gap == 0 else (3 if row_gap == 1 else (1 if row_gap == 2 else 0))

            # If opponent is already on/near the row, prioritize that row's resources even more.
            opp_row_gap = abs(oy - ry)
            opp_row_bias = 2 if opp_row_gap <= 1 else 0

            # If we're closer than opponent, amplify; otherwise, still try to reduce their lead.
            lead_term = (opp_d - our_d)

            cand = lead_term + row_bonus + opp_row_bias - 0.2 * abs(nx - rx)
            if cand > score:
                score = cand

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]