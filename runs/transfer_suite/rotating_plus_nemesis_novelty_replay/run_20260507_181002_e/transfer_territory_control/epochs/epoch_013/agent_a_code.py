def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    oppT = toset(observation.get("opponent_territory"))
    selfT = toset(observation.get("self_territory"))

    if not unclaimed and resources:
        unclaimed = set(resources)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    cand_dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist2(x1, y1, x2, y2):
        dx, dy = x1 - x2, y1 - y2
        return dx * dx + dy * dy

    target_list = []
    if oppT:
        target_list = list(oppT)
    elif unclaimed:
        target_list = list(unclaimed)
    elif resources:
        target_list = list(resources)
    else:
        target_list = [(ox, oy)]

    best_move = (0, 0)
    best_score = None

    for dx, dy in cand_dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        cell = (nx, ny)
        score = 10**9
        if oppT and cell in oppT:
            score = -10**7 + dist2(nx, ny, ox, oy)
        else:
            # Prefer moving toward best target; also avoid wandering back to our territory edges.
            t = min(target_list, key=lambda p: (dist2(nx, ny, p[0], p[1]), p[0], p[1]))
            score = dist2(nx, ny, t[0], t[1])
            if selfT and cell in selfT:
                score += 3
            if unclaimed and cell in unclaimed:
                score -= 2
            if resources and cell in resources:
                score -= 1
            if oppT and cell in oppT:
                score -= 100
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]