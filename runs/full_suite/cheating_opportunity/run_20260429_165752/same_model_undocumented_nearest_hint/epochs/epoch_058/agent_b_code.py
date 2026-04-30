def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])

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

    if not resources:
        resources = [(((W - 1) // 2), ((H - 1) // 2))]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0

    best_resource = resources[0]
    best_key = None
    for rx, ry in resources:
        d_adv = cheb(sx, sy, rx, ry)
        dc = abs(rx - cx) + abs(ry - cy)
        key = (d_adv, dc, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_resource = (rx, ry)

    tx, ty = best_resource
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        center_bias = abs(nx - cx) + abs(ny - cy)
        score = (-dist, center_bias, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    dx, dy = best_move
    if isinstance(dx, int) and isinstance(dy, int) and dx in (-1, 0, 1) and dy in (-1, 0, 1) and ok(sx + dx, sy + dy):
        return [dx, dy]
    for dx, dy in [(0, 0), (0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
        if ok(sx + dx, sy + dy):
            return [int(dx), int(dy)]
    return [0, 0]