def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if 0 <= px < w and 0 <= py < h:
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        comp = do - ds  # positive means we are closer (favorable vs denier)
        cand = (comp, -ds, rx, ry)
        if best is None or cand > best:
            best = cand
    _, _, tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (10**9, 10**9, 10**9, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        nds = md(nx, ny, tx, ty)
        ndo = md(ox, oy, tx, ty)
        # Prefer: reduce our distance to target; if tied, improve our competitiveness next turn.
        ncomp = ndo - nds
        tiebreak = (0 if (dx, dy) != (0, 0) else 1)  # slight preference to move
        cand = (nds, -ncomp, tiebreak, dx, dy)
        if cand < best_move:
            best_move = cand

    dx, dy = int(best_move[3]), int(best_move[4])
    return [dx, dy]