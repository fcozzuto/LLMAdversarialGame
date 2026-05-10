def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    pursuer_self = ("purs" in self_role) or ("hunter" in self_role) or ("chaser" in self_role) or ("pursuer" in self_role)
    pursuer_opp = ("purs" in opp_role) or ("hunter" in opp_role) or ("chaser" in opp_role) or ("pursuer" in opp_role)
    pursue = pursuer_self or (not pursuer_opp)

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def wall_penalty(x, y):
        # Encourage staying away from edges if possible (helps against boundary hits)
        d = min(x, y, w - 1 - x, h - 1 - y)
        return -0.25 * d  # less penalty near edges

    best_move = [0, 0]
    best_score = -10**18 if pursue else 10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        # Mobility: count valid neighbors to avoid traps
        mob = 0
        for ddx, ddy in moves[1:]:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                mob += 1

        # Obstacle proximity penalty (avoid moving next to blocked cells)
        adj_block = 0
        for ddx, ddy in moves[1:]:
            tx, ty = nx + ddx, ny + ddy
            if (tx, ty) in obstacles:
                adj_block += 1

        # Deterministic tie-breaker favors staying deterministic: lexicographic by dx,dy later
        if pursue:
            score = (-dist) + 0.12 * mob - 0.6 * adj_block + wall_penalty(nx, ny)
            if score > best_score:
                best_score, best_move = score, [dx, dy]
            elif score == best_score:
                if (dx, dy) < tuple(best_move):
                    best_move = [dx, dy]
        else:
            score = dist + 0.12 * mob - 0.6 * adj_block + wall_penalty(nx, ny)
            if score < best_score:
                best_score, best_move = score, [dx, dy]
            elif score == best_score:
                if (dx, dy) < tuple(best_move):
                    best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]