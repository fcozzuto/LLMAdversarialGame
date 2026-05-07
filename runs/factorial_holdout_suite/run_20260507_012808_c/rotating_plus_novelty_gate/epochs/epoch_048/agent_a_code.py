def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    if sx < 0: sx = 0
    if sy < 0: sy = 0
    if ox < 0: ox = 0
    if oy < 0: oy = 0
    if sx >= w: sx = w - 1
    if sy >= h: sy = h - 1
    if ox >= w: ox = w - 1
    if oy >= h: oy = h - 1

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in (observation.get("resources") or []):
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = w - 1 - sx, h - 1 - sy
    else:
        best = None
        best_score = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are ahead; otherwise prefer those with maximal potential to arrive sooner.
            score = (opd - myd, -myd, rx, ry)  # deterministic tie-break
            if best is None or score > best_score:
                best, best_score = (rx, ry), score
        tx, ty = best

    # Choose move maximizing advantage after move; avoid stepping into obstacles if possible.
    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_mv = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        val = (opd2 - myd2, -myd2, -abs(nx - (tx)), -abs(ny - (ty)), dx, dy)
        if best_val is None or val > best_val:
            best_val, best_mv = val, (dx, dy)

    if best_val is None:
        return [0, 0]
    return [int(best_mv[0]), int(best_mv[1])]