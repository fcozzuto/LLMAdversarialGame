def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = observation.get("resources") or []
    best_pos = None
    best_dist = 10**9
    for p in resources:
        if p is None or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if (x, y) in obstacles:
            continue
        d = abs(x - sx) + abs(y - sy)
        if d < best_dist:
            best_dist, best_pos = d, (x, y)

    role = (observation.get("self_role") or "").lower()
    is_pursuer = any(k in role for k in ("pursuer", "hunter", "chaser", "pursuit", "attacker"))
    dxs = (-1, 0, 1)
    dys = (-1, 0, 1)

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def score_move(nx, ny):
        if (nx, ny) in obstacles:
            return -10**12
        oppd = abs(nx - ox) + abs(ny - oy)
        resd = None
        if best_pos is not None:
            resd = abs(nx - best_pos[0]) + abs(ny - best_pos[1])
        res_term = 0.0
        if resd is not None:
            res_term = -resd
        if is_pursuer:
            opp_term = oppd * 0.3
        else:
            opp_term = -oppd * 0.7
        return res_term + opp_term

    best_score = -10**18
    best_move = [0, 0]
    for dx in dxs:
        for dy in dys:
            nx, ny = clamp(sx + dx, sy + dy)
            sc = score_move(nx, ny)
            if sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
                best_score = sc
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]