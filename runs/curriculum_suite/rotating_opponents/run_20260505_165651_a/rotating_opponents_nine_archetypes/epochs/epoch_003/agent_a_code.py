def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    if not resources:
        return [0, 0]

    res_list = [tuple(r) for r in resources]
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Opponent "sweep" counter: if opponent shares row/col, prioritize moving away along the other axis.
    same_row = (y == oy)
    same_col = (x == ox)

    best_overall = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        on_res = 1 if (nx, ny) in set(res_list) else 0

        # Choose the resource that gives the best relative advantage from the candidate cell.
        # Tie-break deterministically by coordinates.
        best_adv = -10**18
        for rx, ry in res_list:
            our_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - our_d  # bigger is better (we closer than opponent)
            # slight preference for nearer resources once advantage is similar
            adv2 = adv * 10 - our_d
            if adv2 > best_adv or (adv2 == best_adv and (rx, ry) < (best_overall[1], best_overall[2])):
                best_adv = adv2

        # If opponent is in same row/col, enforce "evasion" to different axis to disrupt sweeps.
        evasion = 0
        if same_row:
            evasion -= abs(ny - oy) * 3
        if same_col:
            evasion -= abs(nx - ox) * 3

        # Prefer staying within board and avoid moving closer to opponent when we aren't winning a resource.
        prox_pen = -man(nx, ny, ox, oy)

        score = on_res * 10000 + best_adv * 20 + evasion + prox_pen
        if score > best_overall[0]:
            best_overall = (score, dx, dy)

    return [best_overall[1], best_overall[2]]