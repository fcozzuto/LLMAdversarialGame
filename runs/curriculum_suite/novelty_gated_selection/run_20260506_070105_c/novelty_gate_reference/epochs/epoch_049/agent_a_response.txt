def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestd, bestmove = None, (0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny): 
                continue
            d = cheb(nx, ny, cx, cy)
            if bestd is None or d < bestd:
                bestd, bestmove = d, (dx, dy)
        return [int(bestmove[0]), int(bestmove[1])]

    # Opponent-aware: prioritize resources where we are (or become) closer than opponent.
    best_score = None
    best_move = (0, 0)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Evaluate best target for this move.
        move_best = None
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Primary: minimize (self_d - opp_d). Secondary: minimize self_d.
            # Slightly prefer targets closer to opponent too (more contention/denial).
            contention = -abs(opp_d - self_d)
            val = (self_d - opp_d, self_d, contention)
            if move_best is None or val < move_best:
                move_best = val
        if move_best is None:
            continue
        # Convert to a single comparable score (smaller tuple is better).
        if best_score is None or move_best < best_score:
            best_score, best_move = move_best, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]