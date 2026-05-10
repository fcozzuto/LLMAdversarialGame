def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp_move(nx, ny, dx, dy):
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return dx, dy
        return 0, 0

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        dx, dy = clamp_move(nx, ny, dx, dy)
        nx, ny = sx + dx, sy + dy

        # Advantage to the best contested resource after this move.
        best_pos = None
        best_neg = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            diff = do - ds  # positive => we're closer than opponent
            key = (diff, -ds, -(rx * 8 + ry))
            if diff > 0:
                best_pos = key if best_pos is None else (key if key > best_pos else best_pos)
            else:
                # If we can't beat anyone this turn, contest the one opponent is closest to.
                key2 = (diff, -do, -ds, -(rx * 8 + ry))
                best_neg = key2 if best_neg is None else (key2 if key2 > best_neg else best_neg)

        if best_pos is not None:
            score = (1, best_pos[0], best_pos[1], best_pos[2])
        else:
            score = (0, best_neg[0], best_neg[1], best_neg[2]) if best_neg is not None else (0, -10**9, 0, 0)

        if best is None or score > best:
            best = score
            best_move = [dx, dy]

    return best_move