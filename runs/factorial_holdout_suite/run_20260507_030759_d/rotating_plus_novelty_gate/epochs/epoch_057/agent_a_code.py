def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources_list = observation.get("resources", []) or []
    resources = set(tuple(r) for r in resources_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    if (sx, sy) in resources:
        return [0, 0]
    if not resources:
        return [0, 0]

    def d1(a, b, c, d):
        return abs(a - c) + abs(b - d)

    best_move = None
    best_val = None
    best_sd = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Choose the resource giving the best "race" advantage
        mv = -10**18
        msd = 10**9
        for rx, ry in resources:
            sd = d1(nx, ny, rx, ry)
            od = d1(nx, ny, ox, oy)
            # Prefer being closer to the resource than opponent, and also faster overall
            val = (od - sd) * 2 - sd
            if val > mv or (val == mv and sd < msd):
                mv = val
                msd = sd
        # Tie-break: prefer moves that are diagonals (usually faster in both axes), then smaller sd
        diag_pref = 1 if dx != 0 and dy != 0 else 0
        cand = (mv, diag_pref, -msd)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]