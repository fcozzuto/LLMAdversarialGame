def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        dx = (1 if ox > sx else -1 if ox < sx else 0)
        dy = (1 if oy > sy else -1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0: 
                    continue
                if valid(sx + ddx, sy + ddy):
                    return [ddx, ddy]
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if valid(sx + dx, sy + dy):
                moves.append((dx, dy))
    if (0, 0) not in moves:
        if valid(sx, sy):
            moves.append((0, 0))

    def target_value(cx, cy, tx, ty):
        ds = cheb(cx, cy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        lead = do - ds
        # Encourage contested wins (positive lead) and also closer pickups.
        return lead * 10 - ds

    best_move = None
    best_score = None
    best_tdist = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        cur_best = None
        cur_tdist = None
        for tx, ty in resources:
            ds = cheb(nx, ny, tx, ty)
            if cur_best is None:
                cur_best = target_value(nx, ny, tx, ty)
                cur_tdist = ds
            else:
                v = target_value(nx, ny, tx, ty)
                if v > cur_best or (v == cur_best and ds < cur_tdist):
                    cur_best = v
                    cur_tdist = ds
        score = cur_best
        if best_score is None or score > best_score or (score == best_score and cur_tdist < best_tdist) or \
           (score == best_score and cur_tdist == best_tdist and (dx, dy) < best_move):
            best_score = score
            best_tdist = cur_tdist
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]