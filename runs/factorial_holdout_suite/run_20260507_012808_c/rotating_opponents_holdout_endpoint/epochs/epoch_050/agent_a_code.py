def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # deterministic tie-break: fixed order above; score then preference for lower myd
    best_move = (0, 0)
    best_score = None
    best_myd = None

    for dx, dy in deltas:
        nx = sx + dx; ny = sy + dy
        if not (0 <= nx < w and 0 <= ny < h):  # avoid relying on engine rejection
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = None
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            opd = cheb(ox, oy, tx, ty)
            # prefer states where we can be earlier; small penalty to keep progress
            val = (opd - myd) * 100 - myd
            if my_best is None or val > my_best:
                my_best = val
        if my_best is None:
            continue
        myd_best = min(cheb(nx, ny, tx, ty) for tx, ty in resources)

        if best_score is None or my_best > best_score or (my_best == best_score and myd_best < best_myd):
            best_score = my_best
            best_myd = myd_best
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]