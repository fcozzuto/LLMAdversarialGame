def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Prefer immediate win pressure, then safety against denier.
    # If resources are plentiful, bias toward closer resources to start contesting.
    scarce = 1 if observation.get("remaining_resource_count", len(resources)) <= 4 else 0
    tie_lag_weight = 3 if scarce else 1

    best_move = [0, 0]
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue

            # Evaluate this state by its best resource contest outcome.
            state_best = None
            for rx, ry in resources:
                sd = man(nx, ny, rx, ry)
                od = man(ox, oy, rx, ry)
                ahead = od - sd  # positive means we arrive earlier
                # Encourage grabbing now (smaller sd), deny opponent (larger od),
                # and avoid giving them a faster line (small ahead is bad).
                # Also slightly prefer cells that are farther from opponent when tie.
                opp_far = man(nx, ny, ox, oy)
                # If we can't beat them, reduce their advantage more than pure proximity.
                key = (
                    0 if ahead > 0 else 1,          # must-beat first
                    -(ahead) if ahead > 0 else -od + sd,  # maximize lead, else reduce their speed advantage
                    sd,                             # then shorter path to the resource
                    -opp_far,                       # then safer from opponent
                    rx, ry                           # deterministic tie-break
                )
                if state_best is None or key < state_best:
                    state_best = key

            # Global choice: maximize contest dominance, with lag-sensitive weight.
            # Slightly favor moving (avoid staying) when contest outcomes are equal.
            move_pen = 0 if (dx == 0 and dy == 0) else -tie_lag_weight * (1 if scarce else 0)
            global_key = (state_best[0], state_best[1] + move_pen, state_best[2], state_best[3], dx, dy)
            if best_key is None or global_key < best_key:
                best_key = global_key
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]