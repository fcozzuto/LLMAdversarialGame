def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def sgn(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [-sgn(ox - x), -sgn(oy - y)]

    # Choose target: prefer resources where we are ahead (opponent farther than us),
    # then prefer closer ones to us.
    best_t = None
    best_key = None
    for r in resources:
        tx, ty = r[0], r[1]
        d_me = abs(tx - x) + abs(ty - y)
        d_opp = abs(tx - ox) + abs(ty - oy)
        lead = d_opp - d_me  # higher is better
        # Key: primary lead, then smaller our distance, then tie-break by coordinates.
        key = (lead, -d_me, -tx, -ty)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (tx, ty)

    tx, ty = best_t
    # Pick move: avoid obstacles; maximize being ahead at next step towards target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or cell_blocked(nx, ny):
            continue
        d_me_new = abs(tx - nx) + abs(ty - ny)
        d_opp_new = abs(tx - (ox + sgn(0))) + abs(ty - (oy + sgn(0)))  # placeholder for opp move term
        # Use current opponent position for opp term (deterministic, no prediction).
        d_opp_cur = abs(tx - ox) + abs(ty - oy)
        lead_new = d_opp_cur - d_me_new
        # Also keep some pressure away from opponent to reduce contesting.
        d_opp_to_us_new = abs((ox) - nx) + abs((oy) - ny)
        d_opp_to_us_cur = abs(ox - x) + abs(oy - y)
        # Val: lead, then closeness to target, then increase separation from opponent.
        val = (lead_new * 1000) - d_me_new + (d_opp_to_us_new - d_opp_to_us_cur) * 0.5
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [dx, dy]