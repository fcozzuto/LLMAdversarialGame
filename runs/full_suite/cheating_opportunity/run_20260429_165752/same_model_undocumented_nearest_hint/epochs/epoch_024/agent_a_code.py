def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target = (W // 2, H // 2)
    if resources:
        best = None
        bd = 10**9
        for r in resources:
            d = dist((sx, sy), r)
            if d < bd:
                bd = d
                best = r
        target = best

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        s = 0
        if resources:
            s -= dist((nx, ny), target)
        s += 0 if (nx, ny) == (ox, oy) else 0
        if (nx, ny) == target:
            s += 1000
        d_op = dist((nx, ny), (ox, oy))
        s += 5 if d_op > 2 else (0 if d_op == 2 else -5)
        if s > best_score or (s == best_score and (dx, dy) < best_move):
            best_score = s
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]