def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(a, b, c, e):
        dx, dy = a - c, b - e
        return dx * dx + dy * dy

    # If no resources: drift to center-ish while avoiding obstacles
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestm = [0, 0]
        for mx, my in cand:
            nx, ny = sx + mx, sy + my
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            k = d2(nx, ny, tx, ty)
            if best is None or k < best:
                best = k
                bestm = [mx, my]
        return bestm if best is not None else [0, 0]

    # Evaluate each move by best "win" margin over opponent among reachable targets
    best_score = None
    best_move = [0, 0]
    for mx, my in cand:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cur_best = None
        # Greedy target choice: pick resource maximizing margin where we are closer than opponent
        for rx, ry in resources:
            self_dist = d2(nx, ny, rx, ry)
            opp_dist = d2(ox, oy, rx, ry)

            # Higher is better: win margin + discourage targets opponent likely to contest immediately
            margin = opp_dist - self_dist  # positive if we are closer
            # Small tie-break to move toward resources sooner (not just denial)
            urgency = -self_dist

            # If opponent already adjacent/at same cell, avoid that unless we can win immediately
            opp_adj_pen = 0
            if d2(ox, oy, rx, ry) == 0:
                opp_adj_pen = -10
            elif d2(ox, oy, rx, ry) <= 2:
                opp_adj_pen = -3

            # Penalize targets that are "unguarded" but very far for us
            far_pen = -0.001 * (self_dist)

            # Favor targets we can plausibly beat: if margin is negative, heavily penalize
            contest_pen = 0
            if margin < 0:
                contest_pen = margin * 2.5  # strong negative

            score = margin + 0.2 * urgency + far_pen + opp_adj_pen + contest_pen

            if cur_best is None or score > cur_best:
                cur_best = score

        # If all resources are bad for this move, cur_best stays numeric due to loop
        if best_score is None or cur_best > best_score:
            best_score = cur_best
            best_move = [mx, my]

    # Fallback (shouldn't happen): stay
    return best_move if best_score is not None else [0, 0]