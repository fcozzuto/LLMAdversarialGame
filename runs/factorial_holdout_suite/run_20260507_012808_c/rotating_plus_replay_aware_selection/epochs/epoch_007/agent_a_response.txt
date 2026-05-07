def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev for diagonal ease

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    # If no resources, drift to our inner corner (minimize path into opponent sweep lanes)
    if not resources:
        tx, ty = 1, h - 2 if sx < w // 2 else 1  # deterministic bias
        cx, cy = w // 2 - 1, h // 2
        target = (cx, cy) if sx <= w // 2 else (w - 2, h // 2)
        best = min(moves, key=lambda m: dist((sx + m[0], sy + m[1]), target))
        return [best[0], best[1]]

    res_set = set(tuple(p) for p in resources)
    alpha = 4.0  # penalize resources the opponent can contest
    beta = 0.5    # small reward for being closer to contested targets

    # Evaluate each immediate move by best achievable resource score from the next cell
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in res_set:
            val = 1e6 - 10 * dist((nx, ny), (ox, oy))  # immediate collection dominates
        else:
            # Choose a deterministic best target based on our advantage after this move
            best_r_val = None
            for rx, ry in resources:
                d_self = dist((nx, ny), (rx, ry))
                d_opp = dist((ox, oy), (rx, ry))
                # Contest penalty: if opponent can reach no later, heavily reduce value
                contest = 1 if d_opp <= d_self else 0
                # Slightly prefer resources that pull us away from the opponent's position
                away = dist((nx, ny), (rx, ry)) + 0.1 * (dist((rx, ry), (ox, oy)))
                r_val = (d_opp - d_self) - alpha * contest + beta * max(0, d_opp - d_self) - 0.05 * away
                # Deterministic tie-break by coordinates
                tie = (rx * 100 + ry)
                r_val = r_val - tie * 1e-6
                if best_r_val is None or r_val > best_r_val:
                    best_r_val = r_val
            val = best_r_val
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]