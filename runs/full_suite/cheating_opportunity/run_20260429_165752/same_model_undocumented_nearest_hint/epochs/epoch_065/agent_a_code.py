def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        # Defensive: move to increase distance from opponent when no resources visible
        best = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            sc = cheb(nx, ny, ox, oy)
            if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best):
                best_score = sc
                best = (dx, dy)
        return [best[0], best[1]]

    best_res = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach sooner; tie-break by being closer to us; then lexicographic.
        key = (opd - myd, -myd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    myd0 = cheb(sx, sy, rx, ry)
    opd0 = cheb(ox, oy, rx, ry)

    # Greedy step with opponent-aware tie-breaking (avoid giving them a faster arrival).
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = cheb(nx, ny, rx, ry)
        # Approximate "who gets there first" after our move (opponent position unchanged this turn).
        score = (opd0 - myd, -myd, -cheb(nx, ny, ox, oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    # If we didn't improve, try to reduce distance to opponent only when that also doesn't worsen our myd.
    if best_move == (0, 0) or cheb(sx + best_move[0], sy + best_move[1], rx, ry) >= myd0:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            myd = cheb(nx, ny, rx, ry)
            if myd > myd0:
                continue
            if myd < myd0 or cheb(nx, ny, ox, oy) > cheb(sx, sy, ox, oy):
                best_move = (dx, dy)
                break

    return [int(best_move[0]), int(best_move[1])]