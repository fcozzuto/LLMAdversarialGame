def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def md(ax, ay, bx, by):
        dx = ax - bx; dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Target selection: prioritize resources where we are likely to be first; also consider steering away from opponent advantage.
    best_t = resources[0]
    best_score = None
    for tx, ty in resources:
        myd = md(sx, sy, tx, ty)
        opd = md(ox, oy, tx, ty)
        # Lower is better: being first helps a lot; if tied, prefer closer one.
        score = (myd - 1.25 * opd, myd, tx, ty)
        if best_score is None or score < best_score:
            best_score = score
            best_t = (tx, ty)

    tx, ty = best_t
    # Choose a move that best improves our chance to secure the chosen target against opponent.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = md(nx, ny, tx, ty)
        opd2 = md(ox, oy, tx, ty)
        # Add a small obstacle-aware term: encourage moves that reduce "threat distance" to opponent via other resources.
        # (Deterministic, light-weight, avoids full search.)
        threat = 0
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            threat += (1 if md(ox, oy, rx, ry) <= md(nx, ny, rx, ry) else 0)
        val = (myd2 - 1.25 * opd2, myd2, threat, dx*dx + dy*dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]