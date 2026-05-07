def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def dist(a, b, c, d):
        return max(abs(c - a), abs(d - b))
    if not resources:
        return [0, 0]

    best_move = (0, 0)
    best_score = -10**18

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        local_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            st = dist(nx, ny, rx, ry)
            ot = dist(ox, oy, rx, ry)
            # Prefer resources we can beat (or tie with slight bias), then maximize time advantage, then smaller st.
            can_win = 1 if st <= ot else 0
            time_adv = ot - st
            value_bias = (rx + ry) * 0.001  # deterministic tie-break
            score = can_win * 1_000_000 + time_adv * 10_000 - st * 10 + value_bias
            # Additional nudge to grab immediate targets
            if st == 0:
                score += 50_000
            elif st == 1 and can_win:
                score += 5_000
            if score > local_best:
                local_best = score
        # Slightly prefer moves that also reduce my distance to nearest resource in case of similar local_best
        my_min = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_min = min(my_min, dist(nx, ny, rx, ry))
        score_move = local_best - my_min
        if score_move > best_score:
            best_score = score_move
            best_move = (mdx, mdy)

    return [int(best_move[0]), int(best_move[1])]