def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for o in obstacles:
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not res:
        return [0, 0]

    # Evaluate each move by how much closer we are than opponent to some resource.
    # Tie-break deterministically by preferring shorter our distance.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        best_diff = None
        best_our = None
        for rx, ry in res:
            our_d = md(nx, ny, rx, ry)
            opp_d = md(ox, oy, rx, ry)
            diff = opp_d - our_d
            if best_diff is None or diff > best_diff or (diff == best_diff and our_d < best_our):
                best_diff = diff
                best_our = our_d

        # Prefer winning races (positive diff). If tied, go for closer resource.
        key = (best_diff, -best_our, -abs(nx - ox) - abs(ny - oy), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]