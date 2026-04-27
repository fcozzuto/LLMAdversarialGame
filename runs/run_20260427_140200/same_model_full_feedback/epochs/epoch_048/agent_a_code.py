def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 8)
    h = int(observation.get("grid_height", 0) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def manh(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if resources:
            dres = min(manh(nx, ny, rx, ry) for rx, ry in resources)
            closest = min(manh(ox, oy, rx, ry) for rx, ry in resources)
            toward = -dres
            steal = 8 if dres < closest else 0
        else:
            toward = 0
            steal = 0
        dop = manh(nx, ny, ox, oy)
        block = 0
        if dop <= 1:
            block = 5
        val = toward + steal + block - 0.2 * dop
        if val > best[0]:
            best = (val, dx, dy)

    return [int(best[1]), int(best[2])]