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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ourd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            gain = oppd - ourd
            key = (-gain, ourd, rx, ry)  # maximize gain, then minimize our distance
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = (W // 2, H // 2)

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ourd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        gain = oppd - ourd
        # Primary: maximize gain, Secondary: minimize our distance, Tertiary: prefer forward-ish
        fwd = (dx != 0 or dy != 0)  # deterministic tie-breaker
        score = (-gain, ourd, 0 if fwd else 1, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move