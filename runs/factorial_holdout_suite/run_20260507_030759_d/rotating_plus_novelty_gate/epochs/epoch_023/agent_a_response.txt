def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if not resources:
        # deterministic "patrol": move to midline of opponent sweep tendencies
        # Prefer shifting x toward opponent; tie by y.
        dx_pref = 1 if ox > sx else (-1 if ox < sx else 0)
        dy_pref = 1 if oy > sy else (-1 if oy < sy else 0)
        best = (0, 0)
        for dx, dy in legal:
            if (dx == dx_pref and dy == dy_pref) or (dx == dx_pref and dy_pref == 0) or (dy == dy_pref and dx_pref == 0):
                best = (dx, dy)
                break
        return [best[0], best[1]]

    # Evaluate best move by choosing the resource that we can reach first relative to opponent,
    # but re-evaluated from the candidate next position (one-step lookahead).
    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def tie_key(rx, ry):
        # deterministic: prefer smaller coordinates
        return rx * 16 + ry

    best_move = None
    best_score = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose best resource for this candidate position
        local_best = -10**18
        for rx, ry in resources:
            d_me = man((nx, ny), (rx, ry))
            d_op = man((ox, oy), (rx, ry))
            # primary: how much closer we are than opponent after this move
            lead = d_op - d_me
            # secondary: prefer actually being closer (smaller d_me)
            closeness = -d_me
            # secondary: slightly prefer resources "in our direction"
            dir_bias = 0
            if (rx - nx == 0 and (ry - ny) != 0) or (ry - ny == 0 and (rx - nx) != 0):
                dir_bias = 1
            v = lead * 200 + closeness * 3 + dir_bias - tie_key(rx, ry) * 0.0001
            if v > local_best:
                local_best = v
        # slight preference to reduce immediate distance to current opponent to contest space
        contest = -man((nx, ny), (ox, oy)) * 0.001
        total = local_best + contest
        if total > best_score:
            best_score = total
            best_move = (dx, dy)
        elif total == best_score:
            # deterministic tie: smaller dx then dy magnitude
            if best_move is None:
                best_move = (dx, dy)
            else:
                if (abs(dx), abs(dy), dx, dy) < (abs(best_move[0]), abs(best_move[1]), best_move[0], best_move[1]):
                    best_move = (dx, dy)

    return [best_move[0], best_move[1]]