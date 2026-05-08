def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    blocked = set()
    for p in obstacles:
        if p is None:
            continue
        try:
            x, y = p[0], p[1]
        except Exception:
            continue
        blocked.add((x, y))
    resources = observation.get("resources") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_dx, best_dy = 0, 0
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in blocked:
            continue
        if resources:
            best_res = None
            for r in resources:
                rx, ry = r[0], r[1]
                ds = abs(nx - rx) + abs(ny - ry)
                do = abs(nx - ox) + abs(ny - oy)
                val = ds - (do // 2)
                if best_res is None or val < best_res:
                    best_res = val
            score = best_res
        else:
            score = (abs(nx - ox) + abs(ny - oy))
        if best_score is None or score < best_score:
            best_score = score
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]