def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        if sd == 0:
            best = (2, 0, rx, ry)
            break
        if sd <= od:
            sc = (1, od - sd, -sd, rx, ry)  # prioritize reachable-first with largest lead
        else:
            sc = (0, -od, sd, rx, ry)      # else: contest where opponent is closest
        if best is None or sc > best:
            best = sc

    _, _, _, tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = cheb(nx, ny, tx, ty)
            od = cheb(ox, oy, tx, ty)
            # If we can reach no later than opponent on this target, favor moves that widen opponent pressure
            if cheb(sx, sy, tx, ty) <= od:
                cand = (nd, -cheb(nx, ny, ox, oy), dx, dy)
            else:
                cand = (nd, -cheb(nx, ny, ox, oy), dx, dy)
            if best_move is None or cand < best_move:
                best_move = cand
    if best_move is None:
        return [0, 0]
    return [best_move[2], best_move[3]]