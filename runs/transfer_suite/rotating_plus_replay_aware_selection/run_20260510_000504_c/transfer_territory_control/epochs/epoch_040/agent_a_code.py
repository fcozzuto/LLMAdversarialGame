def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = set(map(tuple, observation.get("resources") or []))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells") or []))
    self_terr = set(map(tuple, observation.get("self_territory") or []))
    opp_terr = set(map(tuple, observation.get("opponent_territory") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manhattan(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    unclaimed_list = list(unclaimed)
    res_list = list(resources)

    def nearest_dist_to_set(x, y, cells):
        best = 10**9
        for (tx, ty) in cells[:48]:
            d = manhattan(x, y, tx, ty)
            if d < best:
                best = d
                if best == 0:
                    return 0
        return best

    if unclaimed_list:
        target_dist_from = lambda x, y: nearest_dist_to_set(x, y, unclaimed_list)
    elif res_list:
        target_dist_from = lambda x, y: nearest_dist_to_set(x, y, res_list)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target_dist_from = lambda x, y: manhattan(x, y, cx, cy)

    cur_dist = target_dist_from(sx, sy)
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        cell = (nx, ny)
        dist = target_dist_from(nx, ny)
        improve = cur_dist - dist  # positive if getting closer

        if cell in unclaimed:
            base = 1200
        elif cell in opp_terr:
            base = 900  # likely flips on entry
        elif cell in self_terr:
            base = 520
        else:
            base = 300

        # discourage stepping into immediate dead ends near many obstacles
        neigh_obs = 0
        for ddx, ddy in dirs:
            tx, ty = nx + ddx, ny + ddy
            if inb(tx, ty) and (tx, ty) in obstacles:
                neigh_obs += 1

        # push slightly toward unclaimed, and away from opponent if we don't make progress
        opp_dist = nearest_dist_to_set(nx, ny, list(opp_terr)[:48]) if opp_terr else 10**6
        opp_bias = (opp_dist if opp_dist < 10**6 else 0) * (-3)

        score = base + improve * 35 - neigh_obs * 18 + opp_bias * 0.1
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move