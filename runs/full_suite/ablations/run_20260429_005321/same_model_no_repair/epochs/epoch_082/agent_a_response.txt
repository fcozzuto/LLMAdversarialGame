def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, cx, cy)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # Deterministic greedy: pick move that maximizes (opp_dist - my_dist) to best resource
    # with a small tie-break favoring nearer resources overall.
    best_overall = None
    for dx, dy, nx, ny in legal:
        best_for_move = None
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gain = opd - myd  # higher means I can get there first (or keep lead)
            # tie-break: prefer smaller my distance, then prefer higher gain stability
            key = (gain, -myd, -(cheb(nx, ny, w // 2, h // 2)))
            if best_for_move is None or key > best_for_move[0]:
                best_for_move = (key, rx, ry, myd, opd)
        key = best_for_move[0]
        # another tie-break between moves: prefer move that reduces opponent distance to our target less
        rx, ry, myd, opd = best_for_move[1], best_for_move[2], best_for_move[3], best_for_move[4]
        move_key = (key[0], key[1], -abs(cheb(ox, oy, rx, ry) - opd), key[2])
        if best_overall is None or move_key > best_overall[0]:
            best_overall = (move_key, dx, dy)

    return [best_overall[1], best_overall[2]]