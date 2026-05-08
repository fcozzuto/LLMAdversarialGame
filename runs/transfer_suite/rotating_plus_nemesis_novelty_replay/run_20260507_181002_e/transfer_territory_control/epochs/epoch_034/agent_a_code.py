def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if v:
            for p in v:
                if isinstance(p, (list, tuple)) and len(p) >= 2:
                    s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def feasible(dx, dy):
        nx, ny = sx + dx, sy + dy
        return inb(nx, ny) and (nx, ny) not in obstacles

    target = None
    if resources:
        best = None
        for tx, ty in resources:
            if (tx, ty) in obstacles:
                continue
            d = abs(tx - sx) + abs(ty - sy)
            if best is None or d < best:
                best = d
                target = (tx, ty)

    def dist_to(nx, ny, x, y):
        return abs(x - nx) + abs(y - ny)

    # Build deterministic score for each feasible move.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        if not feasible(dx, dy):
            continue
        nx, ny = sx + dx, sy + dy
        if target is not None:
            # Prefer moving closer to nearest resource.
            score = -dist_to(nx, ny, target[0], target[1])
            # Tie-break: prefer not staying still.
            if dx == 0 and dy == 0:
                score -= 0.001
        else:
            # No resources: move toward opponent to contest.
            score = -dist_to(nx, ny, ox, oy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if feasible(0, 0):
        return [int(best_move[0]), int(best_move[1])]
    # If somehow no feasible move selected, return a deterministic safe fallback.
    for dx, dy in moves:
        if feasible(dx, dy):
            return [int(dx), int(dy)]
    return [0, 0]