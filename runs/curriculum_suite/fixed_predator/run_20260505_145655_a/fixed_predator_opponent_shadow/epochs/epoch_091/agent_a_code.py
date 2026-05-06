def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h
    def blocked(nx, ny):
        return (nx, ny) in obstacles

    if not resources:
        return [-sign(ox - x), -sign(oy - y)]

    # Choose target that is likely to be uncontested: maximize (opp_dist - my_dist) with slight tie-break.
    best = None
    best_key = None
    for tx, ty in resources:
        my_d = abs(tx - x) + abs(ty - y)
        opp_d = abs(tx - ox) + abs(ty - oy)
        key = (opp_d - my_d, -my_d, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)
    tx, ty = best

    # One-step planning: pick move that improves my advantage vs opponent toward target.
    best_move = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny) or blocked(nx, ny):
            continue
        my_d = abs(tx - nx) + abs(ty - ny)
        opp_d = abs(tx - ox) + abs(ty - oy)
        # My advantage if I take this step (penalize being farther); encourage also to not reduce advantage.
        val = (opp_d - my_d, -my_d, -abs(ox - nx) - abs(oy - ny))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move