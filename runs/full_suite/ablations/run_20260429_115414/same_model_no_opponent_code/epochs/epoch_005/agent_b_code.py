def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        resources.append((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # prefer resources closer to self than opponent
            # maximize margin; then prefer closer to self; then prefer higher x,y deterministically
            key = (-margin, ds, -rx, -ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dself = cheb(nx, ny, tx, ty)
        # obstacle proximity penalty
        pen_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if (nx + ax, ny + ay) in obstacles:
                    pen_obs += 1
        # modest pressure: discourage moving where opponent is also getting closer to the target
        opp_cur = cheb(ox, oy, tx, ty)
        opp_next = None
        for odx, ody in dirs:
            txo, tyo = ox + odx, oy + ody
            if valid(txo, tyo):
                dd = cheb(txo, tyo, tx, ty)
                if opp_next is None or dd < opp_next:
                    opp_next = dd
        if opp_next is None:
            opp_next = opp_cur
        opp_gain = opp_cur - opp_next  # positive if opponent can get closer next
        score = (-dself) - 0.35 * pen_obs - 0.25 * opp_gain
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]