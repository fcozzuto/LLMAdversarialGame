def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose move that maximizes how far ahead we are across resources, with obstacle avoidance.
    best_move = [0, 0]
    best_score = -10**30
    best_tie = (10**9, 10**9)

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue

            # If moving into obstacle, heavily penalize (engine might keep us in place anyway).
            if (nx, ny) in obstacles:
                continue_pen = True
                score = -10**18
            else:
                continue_pen = False

                # For each resource, compute advantage (opponent farther - us farther).
                # Favor states where we are close and also have larger advantage than opponent.
                max_adv = -10**18
                min_ours = 10**9
                min_opp = 10**9
                for rx, ry in resources:
                    sd = man(nx, ny, rx, ry)
                    od = man(ox, oy, rx, ry)
                    adv = od - sd  # positive if we are closer
                    if adv > max_adv:
                        max_adv = adv
                    if sd < min_ours:
                        min_ours = sd
                    if od < min_opp:
                        min_opp = od

                # Weighted objective: prioritize lead, then being close, then reducing opponent proximity.
                score = 100 * max_adv - 2 * min_ours - 0.5 * min_opp

                # Mild penalty for moving away from the best resource direction.
                # Approx by comparing our distance after move to current best.
                cur_best = 10**9
                for rx, ry in resources:
                    d0 = man(sx, sy, rx, ry)
                    if d0 < cur_best:
                        cur_best = d0
                score -= 0.25 * (min_ours - cur_best)

            tie = (0 if (continue_pen) else 1, man(nx, ny, ox, oy))  # deterministic secondary
            # Primary tie-break uses closeness to nearest resource and then closeness to opponent (to deny)
            # but keep it simple and deterministic.
            if continue_pen:
                # Still allow deterministic selection among all-penalized options (should be rare).
                if score > best_score:
                    best_score = score
                    best_move = [dx, dy]
                continue

            tie2 = (min_ours, min_opp)
            if score > best_score or (score == best_score and (tie2, tie) < (best_tie, (0, 0))):
                best_score = score
                best_move = [dx, dy]
                best_tie = tie2

    return [int(best_move[0]), int(best_move[1])]