def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_blocked(x, y):
        return (x, y) in obstacles

    # Choose a target that we are more likely to secure (advantage), prioritizing nearer resources.
    best_target = None
    best_val = None
    for rx, ry in resources:
        my_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # Advantage: larger means we are closer than opponent.
        # Tie-breaker: prefer smaller my_d to keep tempo.
        val = (opp_d - my_d) * 100 - my_d
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)

    tx, ty = best_target

    # If opponent is much closer to our chosen target, switch to the best alternative with any advantage.
    my_d0 = man(sx, sy, tx, ty)
    opp_d0 = man(ox, oy, tx, ty)
    if opp_d0 - my_d0 > 2:
        best_target = None
        best_val = None
        for rx, ry in resources:
            my_d = man(sx, sy, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d
            # Prefer actual advantage first; if none, take the least-bad.
            val = (adv > 0) * 100000 + adv * 100 - my_d
            if best_val is None or val > best_val:
                best_val = val
                best_target = (rx, ry)
        tx, ty = best_target

    # One-step evaluation: move that maximizes advantage to the chosen target,
    # while also reducing opponent's immediate threat.
    d0_opp = man(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or cell_blocked(nx, ny):
                continue

            my_d = man(nx, ny, tx, ty)
            opp_d = d0_opp  # opponent doesn't move this turn in our heuristic
            advantage = opp_d - my_d

            # Penalty for moving adjacent to opponent (helps vs denial by avoiding easy contests)
            adj_opp = max(abs(nx - ox), abs(ny - oy))
            opp_threat = man(ox, oy, tx, ty) - man(ox, oy, nx, ny)

            # Small obstacle-aware preference: prefer not moving into tight lanes near obstacles.
            obstacle_near = 0
            for ax in (-1, 0, 1):
                for ay in (-1, 0, 1):
                    xx, yy = nx + ax, ny + ay
                    if (xx, yy) in obstacles:
                        obstacle_near += 1

            score = advantage * 200 - my_d * 2 - (1 if adj_opp <= 1 else 0) * 50 + opp_threat * 1 - obstacle_near * 3
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]