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

    def valid(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(x, y, tx, ty):
        d = abs(x - tx) + abs(y - ty)
        if x != tx and y != ty:
            d += 0  # deterministic but equal across diagonals; kept for symmetry
        return d

    if resources:
        tx, ty = min(resources, key=lambda r: (dist(sx, sy, r[0], r[1]), r[0], r[1]))
    else:
        tx, ty = ox, oy

    best = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = dist(nx, ny, tx, ty)
        score2 = dist(nx, ny, ox, oy)
        if (d, score2, dx, dy) < best:
            best = (d, score2, dx, dy)

    if best[2] == 0 and best[3] == 0 and valid(sx, sy):
        return [0, 0]
    if best[2] != 0 or best[3] != 0:
        return [best[2], best[3]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]