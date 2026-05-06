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
        ax -= bx
        if ax < 0:
            ax = -ax
        ay -= by
        if ay < 0:
            ay = -ay
        return ax + ay

    best_move = (0, 0)
    best_val = -10**18

    # Interceptor heuristic:
    # - For each candidate move, look for resources where we can arrive not later than opponent.
    # - Score favors (tight arrival) and (worse arrival for opponent), with a tie-break toward blocking midline.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        val = 0
        for rx, ry in resources:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)

            # Arrival advantage term (only count resources we can realistically steal/secure)
            advantage = opp_d - our_d  # positive is good
            if advantage < 0:
                # Still consider slightly to avoid getting trapped chasing hopeless targets
                val -= (our_d - opp_d) * 2
                continue

            # Strong preference for being as close as possible while denying opponent
            val += 60 * advantage
            val += 8 if our_d == 0 else (6 if our_d == 1 else (3 if our_d == 2 else 0))
            # Row/column blocking pressure: move that aligns with resource while also moving against opponent's direction
            row_gap = abs(ny - ry)
            col_gap = abs(nx - rx)
            val += (5 if row_gap == 0 else 2 if row_gap == 1 else 0)
            val += (3 if col_gap == 0 else 1 if col_gap == 1 else 0)

            # Midline bias: discourage long detours away from opponent's current route
            val += 2 * (abs(nx - ox) < abs(sx - ox) and abs(ny - oy) <= abs(sy - oy))

        # If we can capture something immediately, prioritize it deterministically
        for rx, ry in resources:
            if nx == rx and ny == ry:
                val += 10**6
                break

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]