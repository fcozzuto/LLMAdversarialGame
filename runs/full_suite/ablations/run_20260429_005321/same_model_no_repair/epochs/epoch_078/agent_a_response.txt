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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        # Deterministic "kite" toward the far corner from opponent
        best = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, 0, 0) + cheb(nx, ny, 7, 7) - cheb(nx, ny, ox, oy)
            key = (-v, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    best_move = None
    for dx, dy, nx, ny in legal:
        best_for_move = None
        for i, (rx, ry) in enumerate(resources):
            if (rx, ry) in obst:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer immediate pickup, then create opponent-losing lead.
            pickup = 200 if (nx == rx and ny == ry) else 0
            lead = do - ds
            # If we're behind, strongly discourage that target unless it's immediate.
            behind_pen = 80 if (lead < 0 and pickup == 0) else 0
            # Encourage finishing sooner even if lead is similar.
            val = pickup + 10 * lead - 2 * ds - behind_pen - ((rx + ry + i) & 1)
            if best_for_move is None or val > best_for_move:
                best_for_move = val
        key = (-best_for_move, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]]