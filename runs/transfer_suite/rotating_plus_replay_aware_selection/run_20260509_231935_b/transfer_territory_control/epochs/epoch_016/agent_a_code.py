def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        try:
            obs.add((p[0], p[1]))
        except:
            pass

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        try:
            x, y = p[0], p[1]
            if (x, y) not in obs:
                res.append((x, y))
        except:
            pass

    if res:
        tx, ty = res[0]
        best = abs(tx - sx) + abs(ty - sy)
        for x, y in res[1:]:
            d = abs(x - sx) + abs(y - sy)
            if d < best:
                best = d
                tx, ty = x, y
    else:
        tx, ty = ox, oy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_score = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        score = abs(tx - nx) + abs(ty - ny)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) > best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]