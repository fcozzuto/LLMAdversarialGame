def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    legal = [(dx, dy) for dx, dy in moves if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not resources:
        # Drift away from opponent slightly towards center
        tx, ty = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx, dy in sorted(legal):
            nx, ny = sx + dx, sy + dy
            score = -cheb(nx, ny, tx, ty) + 0.2 * cheb(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)
        return [best[1], best[2]]

    # Choose a resource we are likely to reach first (by relative distance), with deterministic tie-breaks.
    best_target = None
    for rx, ry in sorted(resources):
        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer targets where we are closer than opponent; add slight bias toward nearer overall.
        rel = d_opp - d_self
        overall = -(d_self)
        score = 10 * rel + overall * 0.1 + (1.0 if (rx == ox and ry == oy) else 0.0)
        if best_target is None or score > best_target[0]:
            best_target = (score, rx, ry)
    _, tx, ty = best_target

    # Move that best reduces distance to target, while keeping away from opponent.
    best_move = None
    for dx, dy in sorted(legal):
        nx, ny = sx + dx, sy + dy
        d_to_t = cheb(nx, ny, tx, ty)
        d_from_opp = cheb(nx, ny, ox, oy)
        score = -d_to_t + 0.08 * d_from_opp
        if best_move is None or score > best_move[0]:
            best_move = (score, dx, dy)
    return [best_move[1], best_move[2]]