def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy))
    if not valid:
        return [0, 0]

    if not resources:
        # Head to midpoint, but bias away from opponent
        mx, my = (sx + ox) // 2, (sy + oy) // 2
        best = None
        best_key = None
        for dx, dy in valid:
            nx, ny = sx + dx, sy + dy
            key = (abs(nx - ox) + abs(ny - oy), abs(nx - mx) + abs(ny - my), nx, ny)
            if best_key is None or key < best_key:
                best_key, best = key, (dx, dy)
        return [best[0], best[1]]

    def best_adv_from(x, y):
        # Advantage is how much closer we are than opponent to the closest reachable resource next.
        # Use margin and also prefer nearer overall.
        best = None
        best_key = None
        for rx, ry in resources:
            d1 = abs(rx - x) + abs(ry - y)
            d2 = abs(rx - ox) + abs(ry - oy)
            margin = d2 - d1  # higher is better
            key = (-margin, d1, rx, ry)
            if best_key is None or key < best_key:
                best_key, best = key, margin
        return best

    # 1-step lookahead: pick move whose best future advantage is maximal; tie-break by keeping close to chosen resource.
    best_move = (0, 0)
    best_score = None
    for dx, dy in valid:
        x1, y1 = sx + dx, sy + dy
        # next positions from x1,y1
        next_valid = []
        for ddx, ddy in moves:
            nx, ny = x1 + ddx, y1 + ddy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                next_valid.append((nx, ny))
        if not next_valid:
            next_valid = [(x1, y1)]
        # Evaluate best possible advantage over our immediate next action
        score1 = None
        best_cell = None
        for nx, ny in next_valid:
            adv = best_adv_from(nx, ny)
            key = (-adv, abs(nx - sx) + abs(ny - sy), nx, ny)
            if score1 is None or key < score1:
                score1, best_cell = key, (nx, ny)
        # Outer score favors higher advantage; tie-break by minimizing our distance to the best cell and increasing opponent separation
        opp_sep = abs(best_cell[0] - ox) + abs(best_cell[1] - oy)
        our_dist = abs(best_cell[0] - sx) + abs(best_cell[1] - sy)
        outer_key = (-score1[0] if isinstance(score1, tuple) else -0, -opp_sep, our_dist, dx, dy)
        if best_score is None or outer_key < best_score:
            best_score, best_move = outer_key, (dx, dy)

    return [best_move[0], best_move[1]]