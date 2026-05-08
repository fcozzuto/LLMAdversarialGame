def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    x0, y0 = int(sp[0]), int(sp[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if 0 <= x < w and 0 <= y < h:
                    s.add((x, y))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    if not unclaimed and resources:
        unclaimed = set(resources)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not unclaimed:
        return [0, 0]

    def md(x, y, a, b):
        return abs(x - a) + abs(y - b)

    best_target = None
    best_dist = None
    for tx, ty in unclaimed:
        d = md(x0, y0, tx, ty)
        if best_dist is None or d < best_dist or (d == best_dist and (tx, ty) < best_target):
            best_dist = d
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = x0 + dx, y0 + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        d = md(nx, ny, tx, ty)
        score = (d, 0 if (nx, ny) in unclaimed else 1)
        if best_score is None or score < best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        for dx, dy in moves:
            nx, ny = x0 + dx, y0 + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]