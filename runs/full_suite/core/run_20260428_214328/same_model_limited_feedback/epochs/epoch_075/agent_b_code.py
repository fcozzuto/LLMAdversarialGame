def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        tx, ty = (w // 2, h // 2)
        best = (10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obstacles:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        val = (do - ds) * 10 - ds  # prioritize where we are closer than opponent
        if (rx, ry) == (sx, sy):
            val += 10**9
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    rx, ry = best_target
    best = (10**18, 0, 0)
    # Prefer reducing distance to target; lightly discourage moving into/adjacent to opponent
    for dx, dy in moves:
        nx, ny = clamp(sx + dx, 0, w - 1), clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        d = abs(nx - rx) + abs(ny - ry)
        adj_opp = max(abs(nx - ox), abs(ny - oy))
        score = d * 100 + (0 if adj_opp >= 2 else 5) + (0 if (nx, ny) == (rx, ry) else 0)
        if score < best[0]:
            best = (score, dx, dy)
    return [best[1], best[2]]