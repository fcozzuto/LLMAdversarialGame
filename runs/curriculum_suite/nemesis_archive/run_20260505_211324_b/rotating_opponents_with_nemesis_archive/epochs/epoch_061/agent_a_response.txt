def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []

    obs = set()
    for o in obstacles_in:
        if isinstance(o, (list, tuple)) and len(o) == 2:
            x, y = o[0], o[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) == 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_key = None
    best_move = (0, 0)
    # Evaluate each move by the best resource we can secure (relative advantage over opponent).
    for dx, dy, nx, ny in moves:
        my_pick = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            oppd = man(ox, oy, rx, ry)
            # Prioritize resources closer to us than the opponent (secure), and otherwise still move towards something useful.
            # Slight center bias breaks ties deterministically.
            center_bias = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
            key = (-(oppd - myd), myd, center_bias, rx, ry)
            if my_pick is None or key < my_pick[0]:
                my_pick = (key, rx, ry, myd, oppd)
        key = my_pick[0]
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]