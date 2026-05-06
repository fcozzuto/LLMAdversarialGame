def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx0, cy0 = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def center_bias(x, y):
        dx = x - cx0
        dy = y - cy0
        return -(dx * dx + dy * dy) * 0.02  # slight pull to center

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        step_pen = 0
        if (nx, ny) in obstacles:
            step_pen -= 50  # strong avoid; engine will keep us if blocked
        if not resources:
            val = center_bias(nx, ny)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
            continue

        my_to_opp_next = man(nx, ny, ox, oy)
        val = -my_to_opp_next * 0.1 + center_bias(nx, ny)

        edge_factor = max(nx, w - 1 - nx, ny, h - 1 - ny) / (max(w, h) - 1 + 1e-9)
        # Change: if opponent likely patrols edges, lightly prefer center paths unless we can win a close contest.
        val -= edge_factor * 0.15

        # Resource contest scoring (deterministic aggregation)
        res_score = 0
        for rx, ry in resources:
            dm = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            diff = do - dm  # positive -> we're closer
            # Winning/contesting dominates; denial matters only if we are not already close.
            if dm == 0:
                res_score += 200.0
            else:
                res_score += diff * 10.0 / (1 + dm)
                if diff < 0:
                    res_score += diff * 2.5 / (1 + do)
                # Make contested resources closer to us more attractive
                res_score -= dm * 0.03

        # If opponent is very close, prioritize stepping toward any resource we can beat now
        if my_to_opp_next <= 2:
            for rx, ry in resources:
                dm = man(nx, ny, rx, ry)
                do = man(ox, oy, rx, ry)
                if dm <= do:
                    res_score += (do - dm + 1) * 4.0
                    break

        val += res_score + step_pen
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]