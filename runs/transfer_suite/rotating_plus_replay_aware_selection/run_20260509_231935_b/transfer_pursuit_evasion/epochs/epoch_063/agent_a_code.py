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
    i_am_pursuer = ("pursuer" in self_role) or ("evader" not in self_role and "pursuer" not in opp_role)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    obs_list = list(obs)

    def score_cell(nx, ny):
        d = abs(nx - ox) + abs(ny - oy)
        block = 0
        for ax, ay in obs_list:
            dd = abs(nx - ax) + abs(ny - ay)
            if dd == 0:
                return -10**9
            if dd == 1:
                block += 6
            elif dd == 2:
                block += 2
        # Encourage/avoid distance depending on role; slight preference for center/open space
        center = - (abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.05
        if i_am_pursuer:
            return -d * 10 - block + center
        else:
            return d * 10 - block + center

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        sc = score_cell(nx, ny)
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = sc
            best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]