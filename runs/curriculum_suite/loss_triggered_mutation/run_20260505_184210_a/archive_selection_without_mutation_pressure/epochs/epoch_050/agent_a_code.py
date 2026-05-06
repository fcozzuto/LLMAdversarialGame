def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if resources:
        best = None
        best_gap = None
        best_myd = None
        for rx, ry in resources:
            myd = md(sx, sy, rx, ry)
            od = md(ox, oy, rx, ry)
            gap = od - myd
            if best is None or gap > best_gap or (gap == best_gap and myd < best_myd):
                best = (rx, ry)
                best_gap = gap
                best_myd = myd
        tx, ty = best

        best_move = None
        best_key = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d_to_t = md(nx, ny, tx, ty)
            d_from_opp = md(nx, ny, ox, oy)
            key = (d_to_t, -d_from_opp, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    best_move = None
    best_key = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_from_opp = md(nx, ny, ox, oy)
        key = (-d_from_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]