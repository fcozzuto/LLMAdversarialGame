def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    # If no resources, head to a central position
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = man(nx, ny, cx, cy)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]] if best[1] or best[2] else [0, 0]

    # Row-sweep pressure: prefer moving into rows where the opponent is farther from rich opportunities.
    # Scoring uses "capture advantage" against the opponent over all resources (clipped, to keep local).
    my_best = [0, 0]
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        my_row = ny
        opp_row = oy

        score = 0.0
        # Small center drift to avoid oscillation
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        score -= 0.01 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))

        for (rx, ry) in resources:
            if (rx, ry) in obstacles:
                continue
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)

            # Capture advantage: reward resources where we are closer than opponent.
            # If we are behind, penalize but cap magnitude for robustness.
            adv = opd - myd  # positive is good
            if adv >= 0:
                score += 6.0 / (1 + myd)
            else:
                score += 1.0 * adv / (1 + opd)  # negative, smaller impact

            # Row-sweep interaction: resources on our candidate row help us race if opponent is not aligned.
            if ry == my_row:
                score += 0.8 if my_row != opp_row else 0.2
            if ry == opp_row:
                score -= 0.4 if my_row != opp_row else 0.0

        # Prefer positions that don't get "blocked" by near obstacles (soft avoidance).
        for (ax, ay) in obstacles:
            if man(nx, ny, ax, ay) == 1:
                score -= 1.2

        if score > best_score:
            best_score = score
            my_best = [dx, dy]

    return my_best if (my_best[0] in (-1, 0, 1) and my_best[1] in (-1, 0, 1)) else [0, 0]