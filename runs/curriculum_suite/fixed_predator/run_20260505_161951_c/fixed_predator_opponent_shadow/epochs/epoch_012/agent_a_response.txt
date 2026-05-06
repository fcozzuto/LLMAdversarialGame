def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if not resources:
        best = None
        best_val = -10**18
        for dx, dy, nx, ny in moves:
            d_opp = abs(nx - ox) + abs(ny - oy)
            val = d_opp
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [best[0], best[1]]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = (0, 0)
    best_score = -10**30

    for dx, dy, nx, ny in moves:
        # Choose the best resource we could be "ahead" on after this move.
        best_adv = -10**18
        best_self_d = 10**18
        any_pos_adv = False
        for r in resources:
            rx, ry = r
            sd = abs(nx - rx) + abs(ny - ry)
            od = abs(ox - rx) + abs(oy - ry)
            adv = od - sd
            if adv > 0:
                any_pos_adv = True
                if adv > best_adv or (adv == best_adv and sd < best_self_d):
                    best_adv = adv
                    best_self_d = sd
            elif not any_pos_adv:
                # fallback for when we can't get ahead on any resource
                if sd < best_self_d:
                    best_self_d = sd

        if any_pos_adv:
            score = 10**6 * best_adv - best_self_d
        else:
            score = -best_self_d

        # Small tie-break: move that also reduces opponent proximity (helps avoid racing into same points)
        d_between = abs(nx - ox) + abs(ny - oy)
        score += 0.001 * d_between

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]