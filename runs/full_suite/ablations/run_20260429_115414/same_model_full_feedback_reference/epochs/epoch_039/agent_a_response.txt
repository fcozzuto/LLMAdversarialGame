def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    def kdist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic ordering: prefer staying near center then diagonal
    deltas.sort(key=lambda d: (0 if (d[0] == 0 and d[1] == 0) else 1, abs(d[0]) + abs(d[1]), d[0], d[1]))

    if not resources:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick target resource where we are (most) ahead; otherwise nearest resource.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = kdist(sx, sy, rx, ry)
        od = kdist(ox, oy, rx, ry)
        ahead = od - sd  # positive means we can reach sooner
        # Key: maximize ahead, then minimize our distance, then deterministic tiebreak
        key = (ahead, -sd, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = kdist(nx, ny, tx, ty)
        # Higher is better: reduce distance to target, avoid moving away, break ties deterministically
        score = (-myd, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move