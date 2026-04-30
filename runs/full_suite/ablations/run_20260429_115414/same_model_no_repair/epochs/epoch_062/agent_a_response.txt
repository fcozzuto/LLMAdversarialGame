def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]

    # Maximize a "threat differential" worst-case across resources:
    # prefer moves that reduce opponent access relative to us; if no good lead,
    # pick move that maximizes opponent distance to the closest contested resource.
    best_move = [0, 0]
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        worst = None
        tie_break = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)

            # If we are already advantaged at next step, reward strongly.
            # If we are behind, we try to at least deny by increasing opponent distance.
            # This is evaluated in a single-step greedy way.
            opp_d_after_assumption = dist(ox, oy, rx, ry)
            score = (od - sd) - 0.15 * opp_d_after_assumption

            # worst-case favors robustness
            if worst is None or score < worst:
                worst = score

            # tie-break prefers moves that get us closer to the most "threatening" resource
            threat = od - sd
            if tie_break is None or threat > tie_break:
                tie_break = threat

        # Secondary tie-break: maximize our closeness to the single most threatened resource
        if best_val is None or worst > best_val:
            best_val = worst
            best_move = [dx, dy]
        elif worst == best_val:
            # deterministically choose lower distance sum to avoid oscillations
            cur_sum = 0
            best_sum = 0
            for rx, ry in resources:
                cur_sum += dist(nx, ny, rx, ry)
            bx, by = sx + best_move[0], sy + best_move[1]
            for rx, ry in resources:
                best_sum += dist(bx, by, rx, ry)
            if cur_sum < best_sum:
                best_move = [dx, dy]

    return best_move