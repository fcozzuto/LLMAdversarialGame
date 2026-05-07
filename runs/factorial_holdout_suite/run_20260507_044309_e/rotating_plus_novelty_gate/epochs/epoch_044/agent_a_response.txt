def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(a, b, c, d):
        ax = a - c; ax = ax if ax >= 0 else -ax
        ay = b - d; ay = ay if ay >= 0 else -ay
        return ax + ay

    resources = observation.get("resources", []) or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1, 0) if (ox + oy) > (sx + sy) else (0, h - 1)
        best = (10**9, 10**9, 0, 0)
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = man(nx, ny, tx, ty)
            if d < best[0] or (d == best[0] and i < best[1]):
                best = (d, i, dx, dy)
        return [best[2], best[3]]

    best_val = -10**18
    best_move = (0, 0)
    for i, (dx, dy, nx, ny) in enumerate(valid):
        best_r_val = -10**18
        for (rx, ry) in resources:
            dS = man(nx, ny, rx, ry)
            dO = man(ox, oy, rx, ry)
            lead = dO - dS
            if lead > 0:
                val = 1000 * lead - dS
            else:
                val = -10 * dS + 5 * lead
            if val > best_r_val:
                best_r_val = val
        if best_r_val > best_val or (best_r_val == best_val and i < 0):
            best_val = best_r_val
            best_move = (dx, dy)

    # If tie on selection due to deterministic ordering, pick lexicographically smallest among best-valued moves
    chosen_dx, chosen_dy = best_move
    for i, (dx, dy, nx, ny) in enumerate(valid):
        if (dx, dy) == (chosen_dx, chosen_dy):
            break
    return [chosen_dx, chosen_dy]