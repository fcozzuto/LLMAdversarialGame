def choose_move(observation):
    W = int(observation.get("grid_width") or 8)
    H = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            if legal(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    res = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if legal(x, y):
                res.append((x, y))
    if not res:
        target = observation.get("opponent_position") or [W - 1, H - 1]
        tx, ty = int(target[0]), int(target[1])
    else:
        res.sort()
        tx, ty = min(res, key=lambda r: (dist((sx, sy), r), r[0], r[1]))

    dx = tx - sx
    step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
    dy = ty - sy
    step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

    pref = []
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if legal(nx, ny):
            pref.append((dist((nx, ny), (tx, ty)), mx, my))
    pref.sort()
    for _, mx, my in pref:
        if mx == step_x and my == step_y:
            return [mx, my]
    return [pref[0][1], pref[0][2]]