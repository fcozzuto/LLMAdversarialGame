def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w); h = int(h)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources") or []):
        if r is not None and len(r) >= 2:
            rr = (int(r[0]), int(r[1]))
            if rr not in obstacles:
                resources.append(rr)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_target = resources[0]
    best_key = None
    for tx, ty in resources:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        key = (opd - myd, -myd, tx, ty)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (tx, ty)

    tx, ty = best_target
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = md(nx, ny, tx, ty)
        opd2 = md(ox, oy, tx, ty)
        score = (opd2 - myd2) * 100 - myd2
        if (nx, ny) == (tx, ty):
            score += 10**6
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]

    if not (best_move[0] or best_move[1]):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
    return best_move