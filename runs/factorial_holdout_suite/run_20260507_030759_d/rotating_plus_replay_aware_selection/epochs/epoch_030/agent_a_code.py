def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # diagonal-allowed shortest path length

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = (-10**18, -10**18, 10**18, [0, 0])  # (score, lead, -progress, move)
    nearest_start = 10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        d = dist(sx, sy, rx, ry)
        if d < nearest_start:
            nearest_start = d
    if nearest_start == 10**18:
        nearest_start = 0

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        best_lead_for_move = -10**18
        cnt_winning_targets = 0
        best_target_dist = 10**18

        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            lead = do - ds  # positive means we reach earlier
            if ds < best_target_dist:
                best_target_dist = ds
            if lead > 0:
                cnt_winning_targets += 1
            if lead > best_lead_for_move:
                best_lead_for_move = lead

            # strong bonus for taking a resource immediately
            if ds == 0:
                best_lead_for_move = max(best_lead_for_move, 10**6)

        # progress: prefer reducing distance to closest reachable resource
        progress = nearest_start - best_target_dist

        # combine: maximize winning lead and count, then progress, then avoid staying if equal
        score = best_lead_for_move + 0.15 * cnt_winning_targets
        tie = -1 if (dx == 0 and dy == 0) else 0
        candidate = (score, best_lead_for_move, progress + tie * 0.01, [dx, dy])

        if candidate[0] > best[0] or (candidate[0] == best[0] and (candidate[1] > best[1] or
           (candidate[1] == best[1] and (candidate[2] > best[2])))):
            best = candidate

    return best[3]