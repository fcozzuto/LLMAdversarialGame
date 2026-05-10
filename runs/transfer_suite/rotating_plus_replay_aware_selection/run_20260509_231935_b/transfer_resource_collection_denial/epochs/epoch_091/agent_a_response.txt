def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    res = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    obstacles = {(p[0], p[1]) for p in obs_raw if p and len(p) >= 2}

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def man(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy
    def near_obs(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    if not res:
        best = (None, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            v = -man(nx, ny, ox, oy) - 5 * near_obs(nx, ny)
            if v > best[1]:
                best = ((dx, dy), v)
        if best[0] is None:
            return [0, 0]
        return [best[0][0], best[0][1]]

    resources = [(p[0], p[1]) for p in res if p and len(p) >= 2]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nno = near_obs(nx, ny)
        # Evaluate move by best achievable resource advantage from this next position
        best_cell = -10**18
        for tx, ty in resources:
            ds = man(nx, ny, tx, ty)
            do = man(ox, oy, tx, ty)
            # Prefer immediate collection and deny opponent
            # Tie-break: smaller self distance; higher advantage
            if (nx, ny) == (tx, ty):
                v = 10**6
            else:
                v = (do - ds) * 20 - ds - 6 * nno
            if v > best_cell:
                best_cell = v
        # Small preference to moves that keep cutting toward resources
        v2 = best_cell - 2 * abs((nx - ox)) * 0 - 0
        if v2 > best_val:
            best_val = v2
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]