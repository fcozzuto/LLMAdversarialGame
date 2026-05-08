def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

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
    unclaimed = toset(observation.get("unclaimed_cells") or [])
    resources = toset(observation.get("resources") or [])
    if not unclaimed and resources:
        unclaimed = resources

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    targets = list(unclaimed) if unclaimed else []
    if not targets:
        return [0, 0]

    targets.sort()
    best_t = targets[0]
    best_d = abs(best_t[0] - sx) + abs(best_t[1] - sy)
    for tx, ty in targets[1:]:
        d = abs(tx - sx) + abs(ty - sy)
        if d < best_d:
            best_d, best_t = d, (tx, ty)

    tx, ty = best_t
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = abs(tx - nx) + abs(ty - ny)
        score = (nd, abs(dx) + abs(dy), dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_score is None:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [dx, dy]
        return [0, 0]
    return [best_move[0], best_move[1]]