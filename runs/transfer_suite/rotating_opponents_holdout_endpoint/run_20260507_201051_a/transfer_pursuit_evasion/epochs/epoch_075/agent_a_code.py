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

    resources = observation.get("resources") or []
    best = None
    best_score = None

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        res_min = None
        for r in resources:
            if isinstance(r, (list, tuple)) and len(r) >= 2:
                rx, ry = int(r[0]), int(r[1])
                if 0 <= rx < w and 0 <= ry < h:
                    d = cheb(nx, ny, rx, ry)
                    if res_min is None or d < res_min:
                        res_min = d

        d_opp = cheb(nx, ny, ox, oy)
        score = 0
        if res_min is not None:
            score += (-res_min if is_pursuer else res_min) * 10
        score += (d_opp if not is_pursuer else -d_opp)

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best