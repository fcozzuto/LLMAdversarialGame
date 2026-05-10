def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def is_evader(role):
        r = (role or "").lower()
        return ("evader" in r) or ("runner" in r) or ("evasion" in r) or ("evasive" in r)

    self_evade = is_evader(observation.get("self_role"))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(nx, ny):
        dx = abs(nx - ox)
        dy = abs(ny - oy)
        dist = dx + dy
        # Prefer staying away from obstacles by penalizing moves that reduce local freedom.
        free = 0
        for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            tx, ty = nx + ddx, ny + ddy
            if valid(tx, ty):
                free += 1
        if self_evade:
            return (dist * 100 + free)
        else:
            return (-(dist * 100) + free)

    best = None
    best_val = None
    for ddx, ddy in dirs:
        nx, ny = sx + ddx, sy + ddy
        if not valid(nx, ny):
            nx, ny = sx, sy
        v = score_move(nx, ny)
        if best is None or v > best_val:
            best = [ddx, ddy]
            best_val = v
    return [int(best[0]), int(best[1])]