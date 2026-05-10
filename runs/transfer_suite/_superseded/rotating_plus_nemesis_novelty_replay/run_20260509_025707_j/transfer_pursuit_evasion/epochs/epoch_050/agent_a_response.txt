def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasion" in role) or ("evasive" in role) or ("evade" in role)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def corner_pref(x, y):
        # deterministic tie-breaker that favors moving to a specific far corner based on opponent position
        tx = 0 if ox >= (w - 1) / 2 else (w - 1)
        ty = 0 if oy >= (h - 1) / 2 else (h - 1)
        return (x - tx) * (x - tx) + (y - ty) * (y - ty)

    best_move = [0, 0]
    if not evade:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            diag = 1 if dx != 0 and dy != 0 else 0
            # Primary: minimize Chebyshev (fastest capture with 8-neighbor moves)
            # Secondary: avoid staying if possible, prefer diagonal
            # Tertiary: deterministic corner_pref (slightly helps with obstacles)
            key = (dist, 0 if diag else 1, 1 if (dx == 0 and dy == 0) else 0, corner_pref(nx, ny))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    else:
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dist = cheb(nx, ny, ox, oy)
            diag = 1 if dx != 0 and dy != 0 else 0
            key = (-dist, 0 if diag else 1, 1 if (dx == 0 and dy == 0) else 0, -corner_pref(nx, ny))
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]

    return best_move