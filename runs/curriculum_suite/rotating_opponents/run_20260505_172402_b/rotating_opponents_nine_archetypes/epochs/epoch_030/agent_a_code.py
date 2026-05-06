def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def dist(a, b, x, y):
        dx = a - x
        if dx < 0: dx = -dx
        dy = b - y
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if is_free(nx, ny):
                v = -dist(ox, oy, nx, ny)  # block / approach opponent
                if v > bestv:
                    bestv = v
                    best = [dx, dy]
        return best

    # race resources: maximize (opp_dist - self_dist) after our next move; tie-break by smaller self_dist
    best_move = [0, 0]
    best_val = -10**18
    best_sd = 10**9

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not is_free(nx, ny):
            continue
        my_best_adv = -10**18
        my_best_sd_local = 10**9
        for rx, ry in res:
            sd = dist(sx, sy, rx, ry)  # current self
            sd2 = dist(nx, ny, rx, ry)  # after move
            od = dist(ox, oy, rx, ry)
            adv = (od - sd2)
            # Encourage immediate grabbing by also considering current self progress and closeness after move
            v = adv * 1000 + (sd - sd2) * 10 - sd2
            if v > my_best_adv or (v == my_best_adv and sd2 < my_best_sd_local):
                my_best_adv = v
                my_best_sd_local = sd2
        if my_best_adv > best_val or (my_best_adv == best_val and my_best_sd_local < best_sd):
            best_val = my_best_adv
            best_sd = my_best_sd_local
            best_move = [dx, dy]

    return best_move