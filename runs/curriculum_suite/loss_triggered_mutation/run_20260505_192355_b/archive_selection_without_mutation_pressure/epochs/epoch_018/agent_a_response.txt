def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    if not resources:
        return [0, 0]

    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Favor cells that move us toward a "row-sweep" contested resource (same/adjacent y),
    # while also ensuring we are not far behind the opponent.
    best = (0, 0)
    best_score = -10**18

    for dx in dxs:
        for dy in dys:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue

            # Choose a target resource deterministically for this candidate step.
            best_t = None
            best_t_score = -10**18
            for rx, ry in resources:
                # Contest bias for opponent sweep tendency (horizontal sweeps across a row).
                row_bias = 2 if abs(ry - oy) <= 1 else 0
                # Advantage: being closer than opponent, strongly weighted.
                self_d = man(nx, ny, rx, ry)
                opp_d = man(ox, oy, rx, ry)
                adv = (opp_d - self_d)
                # If opponent is already very close, deprioritize unless we are also close.
                clutch = 0
                if opp_d <= 2 and self_d <= 2:
                    clutch = 3
                elif opp_d <= 2 and self_d > 2:
                    clutch = -3
                # Tie-break: prefer closer target when scores match.
                cand = (3 * adv + row_bias + clutch, -self_d, -abs(rx - nx) - abs(ry - ny), -rx, -ry)
                if cand > (best_t_score, -10**9, -10**9, -10**9, -10**9):
                    best_t_score = cand[0]
                    best_t = (rx, ry)

            # Global score for the move based on chosen target and overall advantage.
            rx, ry = best_t
            self_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            move_score = 4 * (opp_d - self_d) - self_d + (2 if abs(ry - oy) <= 1 else 0)
            move_score += 1 if (man(nx, ny, ox, oy) <= man(sx, sy, ox, oy)) else 0

            if move_score > best_score:
                best_score = move_score
                best = (dx, dy)

    return [int(best[0]), int(best[1])]