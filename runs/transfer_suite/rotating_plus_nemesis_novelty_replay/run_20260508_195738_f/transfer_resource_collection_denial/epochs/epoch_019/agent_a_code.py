def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        tx, ty = w - 1, h - 1
        if ox > sx:
            tx = 0
        if oy > sy:
            ty = 0
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [int(dx), int(dy)]

    # Opponent (nearest_resource archetype) likely targets this resource
    best_opp = None
    best_opp_d = 10**18
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        d = abs(ox - rx) + abs(oy - ry)
        if d < best_opp_d:
            best_opp_d = d
            best_opp = (rx, ry)
    tx, ty = best_opp

    # Prefer moves that create a margin vs the best contested resource
    best_move = None
    best_val = -10**18
    best_tie = 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate best achievable contested resource from this move
        max_margin = -10**18
        chosen_self_d = 10**18
        chosen_opp_d = 10**18
        for rx, ry in resources:
            rx, ry = int(rx), int(ry)
            self_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            margin = opp_d - self_d
            if margin > max_margin or (margin == max_margin and self_d < chosen_self_d):
                max_margin = margin
                chosen_self_d = self_d
                chosen_opp_d = opp_d

        # Additional focus if we can challenge opponent's likely target immediately
        self_d_target = abs(nx - tx) + abs(ny - ty)
        opp_d_target = abs(ox - tx) + abs(oy - ty)
        margin_target = opp_d_target - self_d_target

        # Strongly reward increasing lead margin; penalize distance (faster collection)
        val = max_margin * 100 - chosen_self_d
        # If opponent's target is close, ensure we don't let them win it unchallenged
        val += 30 * (margin_target if margin_target > 0 else 0) - 2 * max(0, -margin_target)

        tie = chosen_self_d + (1 if (nx, ny) == (sx, sy) else 0)
        if val > best_val or (val == best_val and tie < best_tie):
            best_val = val
            best_tie = tie
            best_move = [int(dx), int(dy)]

    if best_move is None:
        return [0, 0]
    return best_move