def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def md(ax, ay, bx, by):
        d = ax - bx
        if d < 0: d = -d
        e = ay - by
        if e < 0: e = -e
        return d + e

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in legal:
            resmin = 10**9
            for rx, ry in resources:
                d = md(nx, ny, rx, ry)
                if d < resmin:
                    resmin = d
            oppd = md(nx, ny, ox, oy)
            on_resource = 1 if (nx, ny) in obstacles and False else 1 if (nx, ny) in resources else 0
            v = -resmin + 0.15 * oppd + 5 * on_resource
            if best is None or v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # No visible resources: maximize distance from opponent, prefer staying closer to center
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = [0, 0]
    bestv = -10**18
    for dx, dy, nx, ny in legal:
        oppd = md(nx, ny, ox, oy)
        cent = abs(nx - cx) + abs(ny - cy)
        v = oppd - 0.01 * cent
        if v > bestv:
            bestv = v
            best = [dx, dy]
    return best