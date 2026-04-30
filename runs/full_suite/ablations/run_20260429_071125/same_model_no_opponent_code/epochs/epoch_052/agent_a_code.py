def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                resources.append((x, y))

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    target = (w // 2, h // 2)
    if resources:
        best = None
        best_score = None
        for tx, ty in resources:
            myd = dist((sx, sy), (tx, ty))
            opd = dist((ox, oy), (tx, ty))
            score = myd - (opd * 0.9)
            if best is None or score < best_score or (score == best_score and (tx, ty) < best):
                best = (tx, ty)
                best_score = score
        target = best

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist((nx, ny), target)
        opd = dist((ox, oy), target)
        # Prefer moving closer, and prefer positions where opponent is relatively farther.
        val = myd - (opd * 0.9)
        # Small tie-break: prefer not moving into being closer to opponent.
        oppd = dist((nx, ny), (ox, oy))
        if best_val is None or val < best_val or (val == best_val and oppd > dist((sx, sy), (ox, oy))):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]