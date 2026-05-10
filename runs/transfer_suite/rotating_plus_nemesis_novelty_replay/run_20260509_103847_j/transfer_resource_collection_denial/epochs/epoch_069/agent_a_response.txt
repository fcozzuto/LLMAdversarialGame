def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # pick a target resource deterministically by a weighted distance race
    best_r = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # prefer resources we can reach earlier; otherwise denier with stronger weight
        win_term = (do - ds)  # positive means we are closer
        # tie-break by smaller opp distance then resource coords
        key = (-win_term, 0 if ds < do else 1, do, rx, ry)
        if best_r is None or key < best_r[0]:
            best_r = (key, (rx, ry))
    tx, ty = best_r[1]

    # Evaluate next moves with one-step obstacle avoidance and continued race heuristic
    best_move = (10**9, 0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        ns = abs(tx - nx) + abs(ty - ny)
        no = abs(tx - ox) + abs(ty - oy)
        # progress towards target, and if we can't beat opponent, still reduce their advantage
        race = (no - ns)
        # also add small preference to move toward any nearby resource
        near = 0
        for rx, ry in resources:
            d = abs(rx - nx) + abs(ry - ny)
            if d == 0:
                near += 50
            elif d <= 2:
                near += (3 - d)
        # avoid staying if not helpful
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # minimize negative score
        score = (-race * 10) + (ns * 2) + stay_pen - near
        key = (score, ns, no, nx, ny)
        if key < best_move:
            best_move = key

    # If all moves blocked, fall back to staying
    return [best_move[3] - sx, best_move[4] - sy] if best_move[1] != 10**9 else [0, 0]