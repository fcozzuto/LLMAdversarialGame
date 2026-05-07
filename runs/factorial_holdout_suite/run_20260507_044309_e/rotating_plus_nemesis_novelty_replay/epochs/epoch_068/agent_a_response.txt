def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set((p[0], p[1]) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = [0, 0]
    best_score = None

    def cell_value(px, py):
        # Prefer resources we can arrive earlier than opponent; add anti-sweep bias by favoring different rows.
        bv = None
        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If ds <= do we have chance; else penalize.
            adv = do - ds
            row_bias = abs(ry - oy)  # sweep_rows tends to stay near its current row; go to different rows
            # Encourage moving toward closer resources only when competitive.
            competitiveness = (adv * 4) + (row_bias) - (ds * 0.15)
            key = (adv, -ds, row_bias, -rx, -ry, competitiveness)
            if bv is None or key > bv[0]:
                bv = (key, (rx, ry))
        return -10**9 if bv is None else bv[0][-1]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sc = cell_value(nx, ny)
        # Deterministic tie-break by move order and resulting coordinates.
        if best_score is None or sc > best_score or (sc == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = sc
            best_move = [dx, dy]

    if best_score is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]