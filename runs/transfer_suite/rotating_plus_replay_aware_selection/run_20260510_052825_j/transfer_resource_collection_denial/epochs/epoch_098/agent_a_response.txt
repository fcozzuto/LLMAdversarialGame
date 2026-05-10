def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = {(int(p[0]), int(p[1])) for p in obstacles_list}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Choose best target resource with a race/tempo heuristic, then pick the move that improves arrival race most.
    best_target = None
    best_score = None
    for rx, ry in resources:
        if not legal(rx, ry):
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Strongly prefer resources where we are closer or can catch up faster.
        race = od - sd  # positive means we are faster (or opponent slower)
        # Penalize being slow in absolute terms to avoid drifting.
        slow_pen = sd
        # Slightly prefer nearer in y-direction to reduce backtracking on typical maps.
        y_pref = (h - 1 - ry) * 0.01
        score = race * 10 - slow_pen + y_pref
        if best_score is None or score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target

    # If we are not actually faster, attempt to "cut" by reducing opponent's lead via the best next step.
    # Evaluate each move by how it changes (opponent_dist - self_dist) toward the target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            nx, ny = sx, sy
        sd2 = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        val = (od - sd2) * 10 - sd2
        # Small tie-break: avoid stepping into positions that increase cheb to the target by more than necessary.
        cur_sd = cheb(sx, sy, rx, ry)
        val -= 0.001 * (sd2 - cur_sd) if sd2 > cur_sd else 0
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]