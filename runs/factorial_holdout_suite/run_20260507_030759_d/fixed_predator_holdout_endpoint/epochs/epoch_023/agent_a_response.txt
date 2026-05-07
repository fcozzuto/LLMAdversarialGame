def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        step_toward = [0, 0]
        tx, ty = w // 2, h // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        step_toward[0], step_toward[1] = dx, dy
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [dx, dy]
        return [0, 0]

    best_move = [0, 0]
    best_val = None  # (primary, secondary, tertiary)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate the best resource this move could secure (advantage over opponent).
        primary_best = None
        secondary_best = None
        tertiary_best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            my_d = dist(nx, ny, rx, ry)
            opp_d = dist(ox, oy, rx, ry)
            primary = opp_d - my_d
            secondary = my_d
            tertiary = dist(nx, ny, ox, oy)
            if primary_best is None or (primary, -secondary, -tertiary) > (primary_best, -secondary_best, -tertiary_best):
                primary_best, secondary_best, tertiary_best = primary, secondary, tertiary

        # Choose move maximizing the advantage, then closest to some resource, then keeping away from opponent.
        cand = (primary_best, -secondary_best, -tertiary_best)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = [dx, dy]

    if best_val is None:
        return [0, 0]
    return best_move