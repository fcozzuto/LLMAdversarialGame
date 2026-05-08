def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    env = str(observation.get("environment_name", "")).lower()
    sr = str(observation.get("self_role", "")).lower()
    orr = str(observation.get("opponent_role", "")).lower()

    is_pursuer = ("pursu" in sr) or ("hunter" in sr)
    if "evasion" in env and (("evad" in sr) or ("escape" in sr) or ("runner" in sr)):
        is_pursuer = False
    if ("pursu" in orr) or ("hunter" in orr):
        is_pursuer = False
    if ("evad" in orr) or ("escape" in orr) or ("runner" in orr):
        is_pursuer = True

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def norm_move(x, y):
        x = 0 if x < 0 else (w - 1 if x >= w else x)
        y = 0 if y < 0 else (h - 1 if y >= h else y)
        return x, y

    corners = [(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if is_pursuer:
        # Chase: minimize distance to opponent
        best = None
        best_d = None
        for dx, dy in moves:
            nx, ny = norm_move(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, ox, oy)
            if best_d is None or d < best_d or (d == best_d and (dx, dy) < best):
                best_d = d
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]
    else:
        # Evade: maximize distance to pursuer, biased to corners
        target_corner = max(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))
        tx, ty = target_corner
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = norm_move(sx + dx, sy + dy)
            if (nx, ny) in obstacles:
                continue
            d_away = cheb(nx, ny, ox, oy)
            d_corner = cheb(nx, ny, tx, ty)
            # Primary: far from pursuer, Secondary: closer to corner
            score = (d_away, -d_corner)
            if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]