def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    target = None
    if resources:
        best = None
        for x, y in resources:
            if x == sx and y == sy:
                best = (0, x, y)
                break
            d = dist(sx, sy, x, y)
            if best is None or d < best[0] or (d == best[0] and (x < best[1] or (x == best[1] and y < best[2]))):
                best = (d, x, y)
        target = (best[1], best[2])

    if target is None:
        tx, ty = (ox, oy)
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        s = dist(nx, ny, tx, ty)
        # Prefer moving closer to target; if tied, prefer not stepping onto opponent
        if (nx, ny) == (ox, oy):
            s += 1000000
        if best_score is None or s < best_score:
            best_score = s
            best_move = [dx, dy]

    return best_move