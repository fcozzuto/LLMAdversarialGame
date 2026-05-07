def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    if not resources:
        return [0, 0]

    def man(ax, ay, bx, by):
        d = ax - bx
        if d < 0:
            d = -d
        e = ay - by
        if e < 0:
            e = -e
        return d + e

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Opponent's likely near-term target (closest resource by manhattan distance)
    best_opp = None
    best_opp_d = 10**9
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp = (rx, ry)
    if best_opp is None:
        return [0, 0]

    # Opponent's greedy next step toward its chosen target (for counter-pressure)
    tx, ty = best_opp
    o_dx = 0 if tx == ox else (1 if tx > ox else -1)
    o_dy = 0 if ty == oy else (1 if ty > oy else -1)
    o_next = (ox + o_dx, oy + o_dy)

    def step_score(nx, ny):
        # Primary: how much closer we are than opponent for our best target (pick single best after moving)
        best_gain = -10**9
        for rx, ry in resources:
            self_d = man(nx, ny, rx, ry)
            opp_d = man(o_next[0], o_next[1], rx, ry)
            gain = opp_d - self_d  # positive means we are closer next turn (by manhattan)
            # Favor taking a resource sooner too (not only relative advantage)
            if gain > best_gain or (gain == best_gain and self_d < best_opp_d):
                best_gain = gain

        # Secondary: avoid walking into obstacles; add mild preference to not go straight into opponent chase line
        opp_next_dist = man(nx, ny, o_next[0], o_next[1])
        # If we move onto opponent's likely target cell, that's extremely strong
        on_opp_path = 1 if resources and (nx, ny) == (tx, ty) else 0
        return best_gain * 10 + opp_next_dist + on_opp_path * 100

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) in set((r[0], r[1]) for r in resources):
            return [dx, dy]
        val = step_score(nx, ny)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]