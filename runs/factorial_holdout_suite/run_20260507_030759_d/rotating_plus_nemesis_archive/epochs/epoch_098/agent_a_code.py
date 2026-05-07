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
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    if (sx, sy) in obstacles:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    def dist(a, b, c, d):
        ddx = a - c
        if ddx < 0: ddx = -ddx
        ddy = b - d
        if ddy < 0: ddy = -ddy
        return ddx + ddy

    if resources:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = None
            for rx, ry in resources:
                d = dist(nx, ny, rx, ry)
                if md is None or d < md:
                    md = d
            score = -md if md is not None else 0
            if best is None or score > best[0]:
                best = (score, dx, dy)
    else:
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = -dist(nx, ny, ox, oy)
            if best is None or score > best[0]:
                best = (score, dx, dy)

    return [best[1], best[2]] if best else [0, 0]