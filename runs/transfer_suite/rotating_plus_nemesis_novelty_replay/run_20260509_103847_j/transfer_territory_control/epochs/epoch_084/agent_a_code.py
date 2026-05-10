def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    target = None
    if resources:
        target = min(resources, key=lambda t: dist(sx, sy, t[0], t[1]))
    else:
        un = []
        for p in observation.get("unclaimed_cells") or []:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if ok(x, y):
                    un.append((x, y))
        if un:
            target = min(un, key=lambda t: dist(sx, sy, t[0], t[1]))
        else:
            target = (sx, sy)

    tx, ty = target
    best = None
    bestv = None
    curD = dist(sx, sy, tx, ty)
    oppD = dist(sx, sy, ox, oy)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        nod = dist(nx, ny, ox, oy)
        score = (curD - nd) * 10 - nd + (nod - oppD) * 2
        if bestv is None or score > bestv or (score == bestv and (dx, dy) < best):
            bestv = score
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]