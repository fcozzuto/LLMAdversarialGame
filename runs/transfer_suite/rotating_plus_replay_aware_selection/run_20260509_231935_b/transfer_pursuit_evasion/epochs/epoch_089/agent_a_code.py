def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("pursu" in self_role) or ("chase" in self_role) or ("hunter" in self_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    # Deterministic preference order: reduce escape/chase first, then center-ward
    pref = [(0,-1), (-1,0), (1,0), (0,1), (-1,-1), (1,-1), (-1,1), (1,1), (0,0)]
    moves = [m for m in pref if m in moves] + [m for m in moves if m not in pref]

    best_move = [0, 0]
    if is_pursuer:
        best = None  # lower is better
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            # Tie-break: keep moves toward opponent in Chebyshev, avoid staying
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            border_pen = (1 if nx in (0, w-1) else 0) + (1 if ny in (0, h-1) else 0)
            score = (d, stay_pen, border_pen)
            if best is None or score < best:
                best = score
                best_move = [dx, dy]
    else:
        best = None  # higher is better
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            # Tie-break: prefer moving away in sign directions; avoid staying if possible
            away_x = 1 if ((nx - ox) * (sx - ox) > 0) else 0
            away_y = 1 if ((ny - oy) * (sy - oy) > 0) else 0
            stay_pen = 1 if (dx == 0 and dy == 0) else 0
            score = (d, away_x + away_y, -stay_pen)
            if best is None or score > best:
                best = score
                best_move = [dx, dy]

    # If all moves invalid (rare), stay
    return [int(best_move[0]), int(best_move[1])]