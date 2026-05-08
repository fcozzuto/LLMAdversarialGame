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

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("purs", "hunt", "chaser", "seeker", "hunter", "pursuer", "catch"))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    def adj_obst_pen(x, y):
        pen = 0
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy) in obstacles:
                pen += 1
        return pen

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            score = -10**9 if is_pursuer else -10**9
        else:
            d2 = dist2(nx, ny, ox, oy)
            pen = adj_obst_pen(nx, ny)
            if is_pursuer:
                score = (-d2) - 0.6 * pen + (2.0 if d2 == 0 else 0.0)
            else:
                score = (d2) - 0.7 * pen + 0.03 * (nx - (w - 1) / 2.0) ** 2 + 0.03 * (ny - (h - 1) / 2.0) ** 2
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move