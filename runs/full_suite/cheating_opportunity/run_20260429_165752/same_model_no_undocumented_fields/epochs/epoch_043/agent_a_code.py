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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = [(dx, dy) for dx, dy in dirs if free(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    # Pick a target resource that we can beat the opponent to (or otherwise is closest)
    if resources:
        best_t = resources[0]
        best_gap = None
        best_self = None
        for tx, ty in resources:
            ds = cheb(sx, sy, tx, ty)
            do = cheb(ox, oy, tx, ty)
            gap = do - ds
            if best_gap is None or gap > best_gap or (gap == best_gap and ds < best_self):
                best_gap = gap
                best_self = ds
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # Evaluate legal moves against target with a "race" heuristic
    best_move = legal[0]
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        ds = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)

        # Encourage reaching target sooner than opponent and slightly penalize moving away
        score = (do - ds) * 100 - ds
        # Slightly prefer moves that increase distance from opponent when we can't win the race
        if resources and (do - ds) < 0:
            score += cheb(nx, ny, ox, oy) * 0.5

        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]