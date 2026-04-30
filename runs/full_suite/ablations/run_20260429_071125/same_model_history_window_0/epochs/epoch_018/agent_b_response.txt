def choose_move(observation):
    gw = observation["grid_width"]
    gh = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (10**9, 10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < gw and 0 <= ny < gh and (nx, ny) not in obstacles:
                d = abs(nx - cx) + abs(ny - cy)
                if (d, nx, ny, dx, dy) < best:
                    best = (d, nx, ny, dx, dy)
        return [best[3], best[4]]
    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    best_res = None
    best_val = -10**9
    best_ds = 10**9
    for r in resources:
        rx, ry = r
        ds = abs(sx - rx) + abs(sy - ry)
        do = abs(ox - rx) + abs(oy - ry)
        val = do - ds  # prefer resources opponent is farther from
        if val > best_val or (val == best_val and ds < best_ds) or (val == best_val and ds == best_ds and (rx + 31 * ry) % 997 < (best_res[0] + 31 * best_res[1]) % 997 if best_res else True):
            best_val = val
            best_ds = ds
            best_res = (rx, ry)
    tx, ty = best_res
    best_move = (10**9, 10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < gw and 0 <= ny < gh) or (nx, ny) in obstacles:
            continue
        d_t = abs(nx - tx) + abs(ny - ty)
        d_o = abs(nx - ox) + abs(ny - oy)
        # prioritize moving closer to target; tie-break by increasing opponent distance
        key = (d_t, -d_o, nx + 100 * ny)
        if key < (best_move[0], best_move[1], best_move[2]):
            best_move = (key[0], -key[1], key[2], dx, dy)
    return [best_move[3], best_move[4]]