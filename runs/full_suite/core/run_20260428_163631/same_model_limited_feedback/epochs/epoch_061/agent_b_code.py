def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])

    def clamp_step(a, b):
        d = b - a
        if d > 0:
            return 1
        if d < 0:
            return -1
        return 0

    def best_target():
        if not resources:
            return None
        best = None
        best_val = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(rx - sx) + abs(ry - sy)
            do = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach no later than opponent; tie-break by shorter distance
            val = (1 if ds <= do else 0, -ds, -do, -((rx - 3.5) ** 2 + (ry - 3.5) ** 2))
            if best_val is None or val > best_val:
                best_val = val
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = target

    dx1 = clamp_step(sx, tx)
    dy1 = clamp_step(sy, ty)

    candidates = []
    # main diagonal/axis approach first
    candidates.append((dx1, dy1))
    # axis-only alternatives
    candidates.append((dx1, 0))
    candidates.append((0, dy1))
    # small detours: try 90-degree rotations around best direction
    if dx1 != 0 and dy1 != 0:
        candidates.append((dx1, -dy1))
        candidates.append((-dx1, dy1))
    # stay last
    candidates.append((0, 0))

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            return [dx, dy]

    return [0, 0]