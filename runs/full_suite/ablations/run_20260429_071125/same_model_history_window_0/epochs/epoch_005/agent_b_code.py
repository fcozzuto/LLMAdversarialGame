def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return False
        if (nx, ny) in obstacles:
            return False
        return True

    # If standing on a resource, prefer to stay (likely collected by engine); otherwise seek.
    if (sx, sy) in set(tuple(p) for p in resources):
        return [0, 0]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if clamp_move(dx, dy)]
    if not moves:
        return [0, 0]

    res_list = [tuple(p) for p in resources]
    opp_dx, opp_dy = 1 if ox > sx else -1 if ox < sx else 0, 1 if oy > sy else -1 if oy < sy else 0

    def sq(a, b): return a * a + b * b

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Resource attraction: pick nearest resource after move
        best_res = 10**9
        for rx, ry in res_list:
            d = sq(rx - nx, ry - ny)
            if d < best_res:
                best_res = d
        # Encourage moving onto a resource tile
        on_res = 1 if (nx, ny) in set(res_list) else 0

        # Opponent pressure: slightly discourage getting closer (avoid contests)
        opp_dist = sq(ox - nx, oy - ny)

        # Small preference for staying aligned with opponent's general direction reversal (deterministic)
        align = 1 if (dx == opp_dx or dy == opp_dy) else 0

        score = (on_res * 10**7) + (-best_res * 10) + (opp_dist * 0.5) + align * 0.1
        # Tie-break deterministically by fixed move ordering
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]