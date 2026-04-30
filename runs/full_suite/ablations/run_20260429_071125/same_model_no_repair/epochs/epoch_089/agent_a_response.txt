def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    best = None
    best_val = None

    opp_corner_bias = 0
    if cheb(sx, sy, 0, 0) <= cheb(sx, sy, w - 1, h - 1):
        opp_corner_bias = 1
    else:
        opp_corner_bias = -1

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Obstacle safety: strongly avoid stepping near obstacles.
        obs_pen = 0
        for ax, ay in obstacles:
            d = cheb(nx, ny, ax, ay)
            if d == 0:
                obs_pen -= 1000
            elif d == 1:
                obs_pen -= 40
            elif d == 2:
                obs_pen -= 8

        # Compete for best resource: prefer where we are closer than opponent.
        best_gain = None
        best_sd = None
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gain = od - sd  # bigger is better (we are closer than them)
            if best_gain is None or gain > best_gain or (gain == best_gain and sd < best_sd):
                best_gain = gain
                best_sd = sd

        # Mild preference for advancing overall and toward likely capture lanes.
        advance = -best_sd
        center_push = 0
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(nx - cx) + abs(ny - cy)
        center_push = -dist_center * 0.01

        # Tie-breaker: consistent ordering, slight bias based on which corner is ours.
        tie = (dx == 0 and dy == 0) * -0.001 + (dx == 1) * 0.0003 + (dy == 1) * 0.0002 + opp_corner_bias * 0.000001

        val = obs_pen + best_gain * 50.0 + advance + center_push + tie

        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]