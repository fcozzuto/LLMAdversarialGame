def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    if not resources:
        tx, ty = (w // 2, h // 2)
    else:
        # Choose a contested resource: prefer those we can reach sooner than opponent.
        best = None
        best_score = None
        for rx, ry in resources:
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            center_bias = -0.05 * (abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2))
            score = (do - ds) * 2.0 + center_bias
            # If we can't clearly win a race, still prefer closer resources.
            score += -0.15 * ds
            if best is None or score > best_score:
                best = (rx, ry)
                best_score = score
        tx, ty = best

    cand = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate candidate: get closer to target; also avoid stepping into "bad" zones near obstacles.
        dist_to_t = abs(tx - nx) + abs(ty - ny)
        # Obstacle proximity penalty (encourages alternate routes).
        prox = 0
        for ox2, oy2 in obstacles:
            d = abs(ox2 - nx) + abs(oy2 - ny)
            if d == 0:
                prox += 5
            elif d == 1:
                prox += 1.5
            elif d == 2:
                prox += 0.5
        # Opponent race pressure: if we can safely take space that keeps distance lead, prefer it.
        my_race = dist_to_t
        opp_race = abs(tx - ox) + abs(ty - oy)
        opp_closer = 1 if opp_race < my_race else 0
        opp_term = 2.0 * (1 - opp_closer)
        # Also slightly prefer moves that increase distance from opponent to reduce contest randomness.
        opp_dist = abs(ox - nx) + abs(oy - ny)
        score = (-dist_to_t * 2.0) + (-prox) + (opp_term) + (0.03 * opp_dist)
        moves.append((score, dx, dy))

    if not moves:
        return [0, 0]
    moves.sort(key=lambda x: (-x[0], x[1], x[2]))
    return [moves[0][1], moves[0][2]]