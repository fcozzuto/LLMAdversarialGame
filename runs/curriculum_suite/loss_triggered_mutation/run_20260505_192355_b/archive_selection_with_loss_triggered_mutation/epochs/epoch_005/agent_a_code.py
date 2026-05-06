def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        dx = 0
        if tx > sx: dx = 1
        elif tx < sx: dx = -1
        dy = 0
        if ty > sy: dy = 1
        elif ty < sy: dy = -1
        return dx, dy

    # Fallback: drift toward opponent side to avoid stalling
    if not res:
        tx = w - 1 if sx < w - 1 else 0
        ty = h - 1 if sy < h - 1 else 0
        dx, dy = step_towards(tx, ty)
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                return [dx, dy]
        return [0, 0]

    # Choose best target resource for us to reach first / deny to opponent
    best_t = None
    best_s = -10**18
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # prefer larger advantage; tie-break on closer to us
        s = (do - ds) * 1000 - ds
        if best_t is None or s > best_s or (s == best_s and ds < cheb(sx, sy, best_t[0], best_t[1])):
            best_s = s
            best_t = (tx, ty)

    tx, ty = best_t
    # Evaluate immediate move by potential improvement toward target and denial factor
    best_move = (0, 0)
    best_val = -10**18
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        ds_new = cheb(nx, ny, tx, ty)
        ds_now = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Encourage reducing our distance, and only go where opponent is not clearly closer
        val = (do - ds_new) * 1000 - ds_new - (ds_now - ds_new) * 2
        # If two moves tie, prefer the one that heads more directly (lower cheb to target)
        if val > best_val or (val == best_val and ds_new < cheb(sx + best_move[0], sy + best_move[1], tx, ty)):
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]