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

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Fallback: move away from opponent if possible, else towards any open cell (deterministic)
        best = None
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            score = d * 100 + (nx * 3 + ny)
            if best_score is None or score > best_score:
                best_score, best = score, (dx, dy)
        return list(best) if best is not None else [0, 0]

    # Target: resource where we are relatively closer than opponent (material strategic change vs simple nearest).
    target = None
    best_rel = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        rel = (opd - myd) * 10 - myd  # prefer where we have advantage and are not too far
        if best_rel is None or rel > best_rel:
            best_rel, target = rel, (rx, ry)

    tx, ty = target
    best = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(nx, ny, ox, oy)
        op_to_target = cheb(ox, oy, tx, ty)

        # Score: minimize distance to target, keep opponent farther, and don't let opponent be closer to target than us.
        # (Use relative advantage after moving.)
        myd0 = cheb(sx, sy, tx, ty)
        rel_after = op_to_target - myd
        score = -myd * 100 + rel_after * 20 + opd * 2 + (nx * 3 + ny) - (myd0 - myd) * 5
        if best_score is None or score > best_score:
            best_score, best = score, (dx, dy)

    return list(best) if best is not None else [0, 0]