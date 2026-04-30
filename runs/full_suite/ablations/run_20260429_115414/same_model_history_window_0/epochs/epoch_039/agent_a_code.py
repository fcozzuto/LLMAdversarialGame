def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    w = observation["grid_width"]
    h = observation["grid_height"]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def sign(a):
        return -1 if a < 0 else (1 if a > 0 else 0)

    # Pick a deterministic target: prefer resources we can reach sooner than opponent
    best = None
    best_val = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dself = (rx - sx) * (rx - sx) + (ry - sy) * (ry - sy)
        dop = (rx - ox) * (rx - ox) + (ry - oy) * (ry - oy)
        dc = (rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)
        val = dself - 0.6 * dop + 0.01 * dc
        if best_val is None or val < best_val or (val == best_val and (rx, ry) < best):
            best_val = val
            best = (rx, ry)

    if best is None:
        # No resources visible; head toward center safely
        tx, ty = int(round(cx)), int(round(cy))
    else:
        tx, ty = best

    desired = (sign(tx - sx), sign(ty - sy))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if dx == 0 and dy == 0:
                continue
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy))
    moves.append((0, 0))

    # Deterministic ordering: prioritize desired delta, then closest to target
    def move_score(md):
        dx, dy = md
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (ox, oy):
            return 10_000_000
        dist = (tx - nx) * (tx - nx) + (ty - ny) * (ty - ny)
        bias = 0
        if md == desired:
            bias = -1000
        return dist + bias

    moves.sort(key=move_score)
    return [int(moves[0][0]), int(moves[0][1])]