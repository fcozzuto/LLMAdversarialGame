def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -md(nx, ny, int(round(cx)), int(round(cy)))
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return list(best) if best is not None else [0, 0]

    opp_dist_cache = {}
    for rx, ry in resources:
        opp_dist_cache[(rx, ry)] = md(ox, oy, rx, ry)

    best_move = [0, 0]
    best_score = None

    # Deterministic tie-break order: moves in given list order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        # Score = prefer resources where we are closer than opponent, else minimize our distance
        score = -10**9
        for rx, ry in resources:
            myd = md(nx, ny, rx, ry)
            opd = opp_dist_cache[(rx, ry)]
            margin = opd - myd  # positive means we're closer
            # Use strong reward for winning race + prefer nearer even when not winning
            cand = 20 * margin - myd
            if cand > score:
                score = cand
        # Secondary: gently keep away from opponent when tie
        score += 0.01 * (md(nx, ny, ox, oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move