def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        best_t = (-10**18, 10**18, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            dcen = md(nx, ny, cx, cy)
            oppd = md(nx, ny, ox, oy)
            # Prefer center, and also try to not get cornered toward opponent.
            t = (-dcen - 0.05 * oppd, dcen, -oppd)
            if t > best_t:
                best_t, best = t, (dx, dy)
        return list(best) if best is not None else [0, 0]

    best = None
    best_key = (-10**18, 10**18, -10**18)

    # For each move, pick the single best resource to pursue/contest.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        best_for_move = (-10**18, 10**18, -10**18)
        for tx, ty in resources:
            sd = md(nx, ny, tx, ty)
            od = md(ox, oy, tx, ty)

            # Gain > 0 means we are closer than opponent (after our move).
            gain = od - sd

            # Score: strongly favor positive gain, then closeness, then prefer resources that are also far from us (to deny).
            score = 7 * gain - sd - 0.15 * od
            # Tie-break: prefer smaller our distance, then larger gain.
            key = (score, -gain, sd)
            if key > (best_for_move[0], best_for_move[1], -best_for_move[2]):
                best_for_move = (score, gain, -sd)

        move_key = (best_for_move[0], best_for_move[2], best_for_move[1])
        # Prefer higher score, then smaller our distance (encoded), then larger gain.
        if move_key > best_key:
            best_key, best = move_key, (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]