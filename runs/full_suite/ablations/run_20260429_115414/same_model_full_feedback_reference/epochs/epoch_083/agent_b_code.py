def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
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

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy, nx, ny in legal:
            # Prefer cells closer to best resource, but avoid giving opponent an easier path
            my_d = 10**9
            op_d = 10**9
            for rx, ry in resources:
                dmy = dist(nx, ny, rx, ry)
                if dmy < my_d: my_d = dmy
                dop = dist(ox, oy, rx, ry)
                if dop < op_d: op_d = dop
            score = (my_d * 10) - (op_d * 2) - (1 if abs(nx - ox) <= 1 and abs(ny - oy) <= 1 else 0)
            if best is None or score < best[0]:
                best = (score, dx, dy)
        return [int(best[1]), int(best[2])]

    cx, cy = (W - 1) // 2, (H - 1) // 2
    best = None
    for dx, dy, nx, ny in legal:
        score = dist(nx, ny, cx, cy) - (1 if dist(nx, ny, ox, oy) <= 1 else 0)
        if best is None or score < best[0]:
            best = (score, dx, dy)
    return [int(best[1]), int(best[2])]