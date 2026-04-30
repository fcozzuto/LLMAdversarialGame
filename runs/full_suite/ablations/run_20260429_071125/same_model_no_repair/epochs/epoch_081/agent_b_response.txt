def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            rx, ry = int(p[0]), int(p[1])
            if (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate best contest target from our next position
        # Score favors: (1) we are closer than opponent, (2) smaller our distance, (3) smaller opponent distance,
        # (4) staying roughly toward center when ties.
        local_best = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # higher is better
            our_far_pen = ds
            opp_far_pen = do
            center_pen = abs(rx - cx) + abs(ry - cy)
            key = (-adv, our_far_pen, opp_far_pen, center_pen, rx, ry)
            if local_best is None or key < local_best:
                local_best = key

        # Also discourage stepping away while opponent is already ahead to avoid oscillation
        # Compare to best possible advantage over resources from current position.
        cur_best = None
        for rx, ry in resources:
            ds0 = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv0 = do - ds0
            key0 = (-adv0, ds0, do, rx, ry)
            if cur_best is None or key0 < cur_best:
                cur_best = key0
        improvement = cur_best[0] - local_best[0]  # non-positive if adv worsens

        score = (local_best, improvement, nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]