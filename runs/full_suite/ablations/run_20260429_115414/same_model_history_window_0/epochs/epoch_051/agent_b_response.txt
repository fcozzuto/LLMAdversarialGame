def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    if not resources:
        dx = 0
        dy = 0
        # deterministic drift: move toward center
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        if x < cx: dx = 1
        elif x > cx: dx = -1
        if y < cy: dy = 1
        elif y > cy: dy = -1
        nx, ny = x + dx, y + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]
        # fallback
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                nx, ny = x + ddx, y + ddy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [ddx, ddy]
        return [0, 0]

    best_target = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        my_d = abs(rx - x) + abs(ry - y)
        opp_d = abs(rx - ox) + abs(ry - oy)
        # Prefer resources where we are closer, then minimize our distance
        val = (opp_d - my_d, -my_d, -rx, -ry)
        if best_val is None or val > best_val:
            best_val = val
            best_target = (rx, ry)
    tx, ty = best_target

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        d = abs(tx - nx) + abs(ty - ny)
        # Small tie-breakers to keep deterministic preference
        score = ( -d, -abs(ox - nx) - abs(oy - ny), -nx, -ny )
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]