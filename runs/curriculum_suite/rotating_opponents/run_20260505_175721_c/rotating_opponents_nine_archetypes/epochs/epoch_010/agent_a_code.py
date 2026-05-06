def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_move = [0, 0]
    best_key = (10**18, 10**18)

    # Target selection: prioritize resources we can reach first; if none, disrupt where opponent is very close.
    target = None
    target_score = -10**18
    for rx, ry in resources:
        d_self = abs(rx - sx) + abs(ry - sy)
        d_opp = abs(rx - ox) + abs(ry - oy)
        # Being closer is good; if opponent is close, pick it to possibly intercept.
        sc = (d_opp - d_self) * 100 - d_self
        if d_opp <= 2:
            sc += 250  # strong disruption preference
        if sc > target_score:
            target_score = sc
            target = (rx, ry)

    tx, ty = target

    # Move scoring: reduce our distance to target, increase opponent's distance to same target,
    # and slightly repel from opponent to avoid getting "raced" on contested pickups.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds = abs(tx - nx) + abs(ty - ny)
        do = abs(tx - ox) + abs(ty - oy)
        do_after = abs(tx - ox - 0) + abs(ty - oy - 0)  # opponent position fixed this turn
        # Encourage states where we are not letting them close the gap too quickly
        contest = (abs(tx - ox) + abs(ty - oy)) - ds
        opp_dist_now = abs(nx - ox) + abs(ny - oy)
        # If we are adjacent, prioritize moving away unless that helps us win the contest
        away_bonus = opp_dist_now if contest <= 0 else 0

        # Key: smaller ds, larger contest, plus away if needed
        key1 = ds
        key2 = -(contest * 10 + away_bonus)
        if (key1, key2) < best_key:
            best_key = (key1, key2)
            best_move = [dx, dy]

    return best_move