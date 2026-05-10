def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obs_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_in:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    candidates = observation.get("unclaimed_cells") or observation.get("resources") or []
    if not candidates:
        candidates = observation.get("self_territory") or []
    if not candidates:
        return [0, 0]

    best = None
    best_key = None
    for x, y in candidates:
        if x is None or y is None:
            continue
        if (x, y) in obstacles:
            continue
        du = abs(x - sx) + abs(y - sy)
        do = abs(x - ox) + abs(y - oy)
        key = (du, -do, x, y)
        if best_key is None or key < best_key:
            best_key = key
            best = (x, y)
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        du = abs(tx - nx) + abs(ty - ny)
        do = abs(ox - nx) + abs(oy - ny)
        key = (du, -do, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)
    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]