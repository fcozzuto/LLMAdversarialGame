def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    if "purs" in self_role:
        is_pursuer = True
    elif "evad" in self_role:
        is_pursuer = False
    else:
        is_pursuer = ("evad" in opp_role) is False

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def cheb(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    def nearest_obst_dist2(x, y):
        best = 10**18
        for (bx, by) in obstacles:
            d = (x - bx) * (x - bx) + (y - by) * (y - by)
            if d < best:
                best = d
        return 0 if best == 10**18 else best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d2 = cheb(nx, ny, ox, oy)
        obst_d2 = nearest_obst_dist2(nx, ny)
        if is_pursuer:
            score = -d2 + 0.02 * obst_d2
        else:
            score = d2 + 0.02 * obst_d2
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]