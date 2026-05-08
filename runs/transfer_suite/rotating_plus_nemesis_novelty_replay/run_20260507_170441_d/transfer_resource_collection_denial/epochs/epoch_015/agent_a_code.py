def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = set(tuple(p) for p in obstacles)

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def d2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    # Choose target resource where we have a relative advantage
    best_r = None
    best_gain = -10**18
    for rx, ry in resources:
        myd = d2(sx, sy, rx, ry)
        opd = d2(ox, oy, rx, ry)
        gain = opd - myd
        if best_r is None or gain > best_gain or (gain == best_gain and (rx, ry) < tuple(best_r)):
            best_gain = gain
            best_r = (rx, ry)
    tx, ty = best_r

    # Also consider denier: pick a move that maximizes our relative closeness after the move
    def obst_pen(x, y):
        if not obstacles:
            return 0
        pen = 0
        for px, py in obst:
            if (x, y) == (px, py):
                return 10**12
            # discourage stepping adjacent
            dd = abs(x - px) + abs(y - py)
            if dd == 0: pen += 10**12
            elif dd == 1: pen += 50
            elif dd == 2: pen += 8
        return pen

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue

        # primary: move closer to our target
        cur_self = d2(sx, sy, tx, ty)
        new_self = d2(nx, ny, tx, ty)
        move_improve = cur_self - new_self

        # secondary: deny opponent by increasing relative advantage on that target,
        # plus small preference for moving closer to the best "contested" resource.
        cur_opp = d2(ox, oy, tx, ty)
        rel = (cur_opp - new_self) - (cur_opp - cur_self)  # simplified relative change

        # contested fallback: compute relative gain to the best resource after move
        cont_best = -10**18
        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            g = opd - myd
            if g > cont_best:
                cont_best = g

        score = move_improve * 1000 + rel * 10 + cont_best - obst_pen(nx, ny)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]