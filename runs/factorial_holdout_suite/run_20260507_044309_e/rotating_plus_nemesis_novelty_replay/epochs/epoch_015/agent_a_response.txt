def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    # Select move that creates the biggest "capture swing" on the best resource:
    # capture swing = (opp_dist - our_dist), with a bonus if we are closer (or tied).
    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        local_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)

            # Prefer immediate/near capture: if we are not behind, strong bonus.
            behind = sd - od  # <=0 means we are at least as close
            capture_bonus = 0
            if behind <= 0:
                # closer first, then tie-break by remaining distance
                capture_bonus = 1000 - sd * 10
            else:
                # if we're behind, reduce how much behind we are
                capture_bonus = -behind * 5

            # Also prefer resources that are relatively urgent for both (smoother contest)
            contest = (od - sd) * 3

            # Extra tiny preference for resources that are farther from opponent baseline,
            # discouraging chasing items opponent is already sitting on.
            opp_urgency = od * 1

            score = capture_bonus + contest - opp_urgency
            if local_best is None or score > local_best:
                local_best = score

        if local_best is None:
            continue

        # Secondary: prefer moves that reduce our distance to the overall best resource option.
        # (Compute quickly for the current move using the closest resource by our distance.)
        closest_self = 10**9
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d = man(nx, ny, rx, ry)
            if d < closest_self:
                closest_self = d
        move_score = (local_best, -closest_self)
        if best_score is None or move_score > best_score:
            best_score = move_score
            best_move = [dx, dy]

    return best_move