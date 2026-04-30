def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    best = None
    bestkey = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach first; if none, prefer those where opponent is far.
        if dme <= dop:
            key = (0, dme, dop, rx, ry)
        else:
            key = (1, dop - dme, dop, rx, ry)
        if best is None or key < bestkey:
            best = (rx, ry)
            bestkey = key
    tx, ty = best

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    oppd0 = cheb(ox, oy, tx, ty)
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_after = cheb(nx, ny, tx, ty)
        oppd_after = cheb(ox, oy, tx, ty)
        # Extra pressure: move that brings us closer and doesn't allow the opponent to become relatively closer (estimated via our distance only).
        pressure = d_after
        cell_bonus = 1000 if (nx, ny) == (tx, ty) else 0
        # Use our new distance; deterministic tie-breaking by dx,dy order via key
        score = -pressure * 10 + cell_bonus + (oppd0 - oppd_after)
        candidates.append((score, nx, ny, dx, dy))
    candidates.sort(key=lambda t: (-(t[0]), t[3], t[4], t[1], t[2]))
    if not candidates:
        return [0, 0]
    return [candidates[0][3], candidates[0][4]]