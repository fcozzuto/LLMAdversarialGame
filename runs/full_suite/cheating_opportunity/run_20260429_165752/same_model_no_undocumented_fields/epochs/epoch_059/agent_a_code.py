def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if free(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            md = None
            for rx, ry in resources:
                d = cheb(nx, ny, rx, ry)
                if md is None or d < md:
                    md = d
            od = cheb(nx, ny, ox, oy)
            # minimize resource distance; maximize opponent distance; then prefer moving (tie-break by md then od then dx,dy)
            key = (md, -od, abs(dx) + abs(dy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best = [dx, dy]
        return best if best is not None else [0, 0]

    cx, cy = w // 2, h // 2
    best = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        dcenter = cheb(nx, ny, cx, cy)
        od = cheb(nx, ny, ox, oy)
        key = (dcenter, -od, abs(dx) + abs(dy), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]
    return best