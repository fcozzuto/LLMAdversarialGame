def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Target selection: prefer resources where we are closer than opponent; if none, prefer where we can catch up.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # adv>0 means we are closer. Strongly prefer positive adv; break ties by myd then by coordinate.
        adv = opd - myd
        key = (-1 if adv > 0 else 0, -adv, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    myd0 = cheb(sx, sy, tx, ty)
    opd0 = cheb(ox, oy, tx, ty)

    # Opponent-interference: if opponent is close to some resource, bias moves that increase distance to that resource less for us than for them.
    interferes = None
    for rx, ry in resources:
        opd = cheb(ox, oy, rx, ry)
        if interferes is None or opd < interferes[0]:
            interferes = (opd, rx, ry)
    _, ix, iy = interferes

    def clamp_move(nx, ny):
        return (nx, ny) not in obstacles

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Evaluate: want smaller myd; also if we can't beat opponent, try to at least not fall further behind.
        behind = (opd - myd)
        # Interference: reduce opponent's advantage on nearest resource to them.
        myd_i = cheb(nx, ny, ix, iy)
        opd_i = cheb(ox, oy, ix, iy)
        myd_i_effect = myd_i - (opd_i - myd_i)  # monotone-ish; discourages giving opponent a shortcut
        # Deterministic tie-breaking by dx,dy.
        key = (1 if myd > myd0 else 0, -1 if behind > opd0 - myd0 else 0, myd, -behind, myd_i_effect, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]