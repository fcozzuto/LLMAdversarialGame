def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    self_role = (observation.get("self_role") or "").lower()
    opp_role = (observation.get("opponent_role") or "").lower()
    env = (observation.get("environment_name") or "").lower()
    i_am_pursuer = ("pursuer" in self_role) or ("pursuit" in env) or ("pursuer" in opp_role)
    if ("evader" in self_role) or ("evader" in opp_role):
        i_am_pursuer = False

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def d2(x, y, x2, y2):
        dx, dy = x - x2, y - y2
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    # Prefer moving away/toward but also steer to a more "open" area to avoid getting boxed.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dist = d2(nx, ny, ox, oy)

        # openness: count legal neighboring cells (incl self move target)
        open_cnt = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) not in obs:
                open_cnt += 1

        # wall penalty to reduce sticking at edges as evader; reverse for pursuer slight.
        wall_pen = 0
        if nx == 0: wall_pen += 1
        if nx == w - 1: wall_pen += 1
        if ny == 0: wall_pen += 1
        if ny == h - 1: wall_pen += 1

        # pursuer: minimize distance, maximize openness; evader: maximize distance, maximize openness too.
        if i_am_pursuer:
            val = (-dist * 1.0) + (open_cnt * 0.15) + (-wall_pen * 0.02)
            better = (best_val is None) or (val > best_val)
        else:
            val = (dist * 1.0) + (open_cnt * 0.15) + (-wall_pen * 0.02)
            better = (best_val is None) or (val > best_val)

        if better:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]