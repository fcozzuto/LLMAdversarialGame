def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacles = set(map(tuple, observation.get("obstacles", [])))
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))

    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 1.15 if opp_cnt >= self_cnt else 0.7

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    # Pick a target: prefer nearest opponent territory cell; else nearest unclaimed; else opponent.
    if opp_t:
        tx, ty = min(opp_t, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy)))
    else:
        uc = list(unclaimed)
        if uc:
            tx, ty = min(uc, key=lambda p: (abs(p[0] - sx) + abs(p[1] - sy)))
        else:
            tx, ty = ox, oy

    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        score = - (abs(nx - tx) + abs(ny - ty))

        if (nx, ny) in opp_t:
            score += 6000 * aggressive
        elif (nx, ny) in unclaimed:
            score += 1400
        elif (nx, ny) in self_t:
            score += 20

        # Mild wall-following/escape from nearby obstacles
        obs_adj = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if 0 <= xx < w and 0 <= yy < h and (xx, yy) in obstacles:
                    obs_adj += 1
        score -= 35 * obs_adj

        # Prefer advancing into new territory by clustering near unclaimed when not attacking
        if not opp_t and unclaimed:
            # Manhattan to closest unclaimed from candidate
            score += -min(abs(nx - ux) + abs(ny - uy) for (ux, uy) in unclaimed) * 3

        if score > best_score or (score == best_score and [dx, dy] < best_move):
            best_score = score
            best_move = [dx, dy]

    return best_move