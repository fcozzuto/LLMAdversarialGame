def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(nx, ny):
        return 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    cx, cy = W // 2, H // 2

    if resources:
        # Choose a target resource that we are relatively advantaged for.
        best_r = None
        best_rel = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            rel = ds - 0.85 * do
            if best_rel is None or rel < best_rel:
                best_rel = rel
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = cx, cy

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds_new = cheb(nx, ny, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # Prefer lowering our distance to the target while keeping/creating advantage.
        score = -ds_new + 0.35 * do + 0.02 * (-manh(nx, ny, cx, cy))
        # Small tie-break: prefer staying closer to current.
        score += -0.01 * cheb(nx, ny, sx, sy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move