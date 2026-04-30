def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    try:
        w = int(w)
        h = int(h)
        sx, sy = int(sp[0]), int(sp[1])
        ox, oy = int(op[0]), int(op[1])
    except Exception:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    resset = set()
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
                resset.add((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles or not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_r = None
    best_s = -10**18
    for rx, ry in resources:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        pref = 1 if sd <= od else 0
        s = pref * (100000 - 10 * sd) + (od - sd)
        if s > best_s or (s == best_s and (rx, ry) < best_r):
            best_s = s
            best_r = (rx, ry)

    rx, ry = best_r
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_ms = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = man(nx, ny, rx, ry)
        ms = -d
        if (nx, ny) == (rx, ry):
            ms += 10000
        od = man(nx, ny, ox, oy)
        ms += -2 * (od > 0 and od < man(sx, sy, ox, oy))
        if best_m is None or ms > best_ms or (ms == best_ms and (dx, dy) < best_m):
            best_ms = ms
            best_m = (dx, dy)

    return [best_m[0], best_m[1]] if best_m else [0, 0]