def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

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
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        our_win_resources = []
        for rx, ry in resources:
            if cheb(sx, sy, rx, ry) < cheb(ox, oy, rx, ry):
                our_win_resources.append((rx, ry))
        candidates = our_win_resources if our_win_resources else resources

        best = None
        for dx, dy, nx, ny in legal:
            d_to_opp = cheb(nx, ny, ox, oy)
            best_rel = -10**9
            for rx, ry in candidates:
                our_d = cheb(nx, ny, rx, ry)
                opp_d = cheb(ox, oy, rx, ry)
                rel = opp_d - our_d  # positive means we are closer than opponent to that resource
                val = rel * 100 - our_d
                if val > best_rel:
                    best_rel = val
            # Tie-break deterministically by preferring larger distance to opponent, then smaller dx/dy order
            score = best_rel + d_to_opp * 0.01 - (abs(dx) + abs(dy)) * 0.001
            key = (score, d_to_opp, -abs(dx), -abs(dy), dx, dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1]

    # No resources: drift to maximize opponent distance while staying legal
    best = None
    for dx, dy, nx, ny in legal:
        d_to_opp = cheb(nx, ny, ox, oy)
        key = (d_to_opp, -abs(dx), -abs(dy), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])
    return best[1]