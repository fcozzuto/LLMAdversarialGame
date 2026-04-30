def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []) if p and len(p) >= 2)
    resources = [tuple(p) for p in (observation.get("resources") or []) if p and len(p) >= 2]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny): 
                continue
            # prefer center with minimal cheb
            if cheb(nx, ny, tx, ty) == min(cheb(sx + mx, sy + my, tx, ty) for mx, my in moves if safe(sx + mx, sy + my)):
                return [dx, dy]
        return [0, 0]

    # Choose move maximizing advantage in reaching the best available resource this turn.
    best = None  # (gain, myd, oppd, -rx, -ry, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        # Evaluate best resource after move; also consider worst-case (opponent could steal).
        best_loc = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gain = opd - myd  # positive means we are closer
            # Secondary: prefer resources nearer to us
            key = (gain, -myd, -opd, -rx, -ry)
            if best_loc is None or key > best_loc[0]:
                best_loc = (key, myd, opd, rx, ry)
        if best_loc is None:
            continue
        key, myd, opd, rx, ry = best_loc
        overall = (key[0], myd, -opd, -rx, -ry, dx, dy)
        if best is None or overall > best:
            best = overall

    if best is None:
        return [0, 0]
    return [best[-2], best[-1]]