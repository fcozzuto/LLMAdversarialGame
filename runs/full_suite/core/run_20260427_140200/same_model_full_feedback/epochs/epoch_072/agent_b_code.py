def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
    if not resources:
        resources = [(ox, oy)]

    tx = sx
    ty = sy
    best = -10**9

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            val = 0
            rbest = 10**9
            orbest = 10**9
            for rx, ry in resources:
                dr = dist(nx, ny, rx, ry)
                do = dist(ox, oy, rx, ry)
                if dr < rbest:
                    rbest = dr
                if do < orbest:
                    orbest = do
            val += 1000 - 20 * rbest
            val += 10 * (orbest - rbest)
            val += -dist(nx, ny, ox, oy)
            if val > best or (val == best and (nx, ny) < (tx, ty)):
                best = val
                tx, ty = nx, ny

    return [tx - sx, ty - sy]