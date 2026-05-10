def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    role = str(observation.get("self_role") or "").lower()
    pursuer = ("pursu" in role) or ("chase" in role) or ("capt" in role)
    evader = ("evad" in role) or ("escap" in role)
    if not pursuer and evader:
        pursuer = False
    if not pursuer and not evader:
        pursuer = True

    obs_set = set()
    for p in observation.get("obstacles") or []:
        try:
            if isinstance(p, dict):
                x, y = int(p.get("x", -1)), int(p.get("y", -1))
            else:
                x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs_set.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(x, y):
        dx, dy = x - ox, y - oy
        return dx * dx + dy * dy

    def obstacle_pen(x, y):
        if (x, y) in obs_set:
            return 10000
        pen = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (x + ax, y + ay) in obs_set:
                    pen += 3
        return pen

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        d = dist2(nx, ny)
        pen = obstacle_pen(nx, ny)
        # pursuer: minimize distance, evader: maximize distance
        score = (-d if pursuer else d) - pen
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move