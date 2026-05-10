def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]
    tr = observation.get("turns_remaining", 0)
    if not resources:
        return [0, 0]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cell_score_for_target(my_d, opp_d, pick_d):
        # Prefer targets where we are strictly closer; still move if we can tie soon.
        gap = opp_d - my_d
        # Penalize long distance; slight preference for earlier collection.
        return gap * 12 - my_d * 2 + (2 if (pick_d <= tr) else -1)

    best_move = [0, 0]
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_target_val = -10**18
        for r in resources:
            if r is None or len(r) < 2:
                continue
            rx, ry = r[0], r[1]
            if (rx, ry) in obstacles:
                continue
            my_d = man(nx, ny, rx, ry)
            if my_d < 0:
                continue
            opp_d = man(ox, oy, rx, ry)

            # Urgency boost if we can reach before opponent (or within 1 step if close).
            reach_delta = opp_d - my_d
            urgency = 8 if reach_delta >= 1 else (2 if reach_delta == 0 else -4)
            val = cell_score_for_target(my_d, opp_d, my_d) + urgency

            # If many targets are similar, deterministically break ties by coordinates.
            val = val - (rx * 0.01 + ry * 0.001)

            if val > best_target_val:
                best_target_val = val

        # If all resources look losing from this move, still pick the least bad.
        if best_target_val > best_val:
            best_val = best_target_val
            best_move = [dx, dy]

    return best_move