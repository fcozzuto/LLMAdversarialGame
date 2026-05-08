def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    turns_remaining = observation.get("turns_remaining", 0)

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if (sx, sy) in obs:
        return [0, 0]

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    # Pick a target we can "steal" (prefer positive gap), otherwise the best overall.
    best_t = None
    best_key = None
    for rx, ry in res:
        dself = md((sx, sy), (rx, ry))
        dopp = md((ox, oy), (rx, ry))
        gap = dopp - dself  # positive means we are closer now
        # Encourage closer arrival and stronger gap; slight prefer nearer to mid-game.
        key = (gap, -dself, -((turns_remaining if turns_remaining else 0) - dself))
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    target_dist = md((sx, sy), (rx, ry))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    # If already on a resource (environment collects), stay (or move would be rejected).
    if (sx, sy) == (rx, ry):
        return [0, 0]

    # Map for quick "will we capture something" scoring.
    res_set = set(res)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        dnew = md((nx, ny), (rx, ry))
        # Opponent future gap estimate: assume both move 1 step toward same target.
        opp_dnew_est = max(md((ox, oy), (rx, ry)) - 1, 0)
        # But we care relative: use current opponent distance (deterministic, cheap).
        opp_now = md((ox, oy), (rx, ry))
        gap_after = opp_now - dnew

        # Primary: win the race / reduce target distance.
        val = gap_after * 100 - dnew

        # If this move captures any resource, huge bonus; prefer captures closer than target.
        if (nx, ny) in res_set:
            val += 10_000
        # Secondary: if target race is unfavorable, keep from letting opponent gain by moving away slightly.
        val += -md((nx, ny), (ox, oy)) * (1 if best_key[0] <= 0 else 0.1)

        # Small deterministic preference to avoid jitter: favor moves that reduce our distance to target.
        if dnew < target_dist:
            val += 1

        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]