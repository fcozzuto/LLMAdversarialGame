def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            r = (int(p[0]), int(p[1]))
            if r not in obstacles:
                resources.append(r)

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = None

    legal_moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obstacles:
            legal_moves.append((dx, dy, nx, ny))
    if not legal_moves:
        return [0, 0]

    if resources:
        for dx, dy, nx, ny in legal_moves:
            # Race heuristic: prefer resources where we close the gap vs opponent.
            smin = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                v = od - sd  # higher is better
                if smin is None or v > smin:
                    smin = v
            # Small tie-break: also prefer closer-to-resource among the best-v moves
            tclose = 0
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                if resources:
                    if tclose == 0 or sd < tclose:
                        tclose = sd
            score = (smin, -tclose, -abs(dx), -abs(dy), dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
    else:
        # No visible resources: drift toward center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy, nx, ny in legal_moves:
            dist = cheb(nx, ny, cx, cy)
            score = (-dist, dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]