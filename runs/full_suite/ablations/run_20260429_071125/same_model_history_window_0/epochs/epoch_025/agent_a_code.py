def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    ti = observation["turn_index"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        best = (10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                opp = md(nx, ny, ox, oy)
                val = -opp
                if val < best[0]:
                    best = (val, dx, dy)
        return [0, 0] if best[0] == 10**9 else [best[1], best[2]]

    even = (ti % 2 == 0)
    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        if even:
            key = ds + 0.35 * do
        else:
            key = ds - 0.45 * do
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    best = (10**18, 0, 0)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            ds2 = md(nx, ny, rx, ry)
            do2 = md(nx, ny, ox, oy)
            on_resource = 1 if (nx, ny) == (rx, ry) else 0
            # Encourage picking target, avoid allowing opponent immediate access, and keep distance
            penalty_block = 0
            if do2 <= 1:
                penalty_block = 3.0
            # Small tie-break based on turn to avoid repeating exact ties
            tie = 0.01 * ((dx + 1) * 3 + (dy + 1) + (ti % 3))
            val = ds2 - 0.9 * on_resource + penalty_block - (0.08 * do2) + tie
            if val < best[0]:
                best = (val, dx, dy)

    return [best[1], best[2]] if not (best[1] == 0 and best[2] == 0 and best[0] >= 10**17) else [0, 0]