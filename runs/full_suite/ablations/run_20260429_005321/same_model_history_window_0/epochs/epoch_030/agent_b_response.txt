def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        tx, ty = (w // 2, h // 2)
        moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                d = abs(tx - nx) + abs(ty - ny) + 0.01 * ((nx - ox) ** 2 + (ny - oy) ** 2)
                key = (d, dx, dy)
                if key < best:
                    best = key
        return [best[1], best[2]]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        score = 0.0
        d_opp_next = dist(nx, ny, ox, oy)
        score -= 0.03 * d_opp_next
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            # Prefer resources closer to us; penalize if opponent is already closer.
            urgency = 1.0 / (1 + ds)
            contest = (1 + do) / (1 + ds)
            score += 10.0 * urgency * (1.0 if contest <= 1.0 else 1.0 / contest)
            if (nx, ny) == (rx, ry):
                score += 50.0
        key = (score, -dx, -dy)  # deterministic tie-break
        if key > (best_score, -best_move[0], -best_move[1]):
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]