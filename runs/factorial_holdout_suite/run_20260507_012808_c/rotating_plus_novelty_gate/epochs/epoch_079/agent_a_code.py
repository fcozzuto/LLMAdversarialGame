def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        try:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources") or []:
        try:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
        except:
            pass

    if not resources:
        return [0, 0]

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Prefer resources where we are relatively closer than opponent; also bias to nearer ones.
    best = None
    for rx, ry in resources:
        sd = md(sx, sy, rx, ry)
        od = md(ox, oy, rx, ry)
        rel = od - sd  # larger is better: opponent farther than us
        key = (rel, -sd, -(rx + ry))  # deterministic tie-break
        if best is None or key > best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (-dx, 0), (0, -dy), (0, 0)]
    for cdx, cdy in candidates:
        nx, ny = sx + cdx, sy + cdy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return [int(cdx), int(cdy)]

    return [0, 0]