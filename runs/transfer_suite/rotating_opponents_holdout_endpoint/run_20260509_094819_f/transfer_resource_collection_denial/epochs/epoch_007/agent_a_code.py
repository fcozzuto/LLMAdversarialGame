def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            res.append((int(p[0]), int(p[1])))

    if not res:
        dx = 0
        if sx < w // 2:
            dx = 1
        elif sx > w // 2:
            dx = -1
        dy = 0
        if sy < h // 2:
            dy = 1
        elif sy > h // 2:
            dy = -1
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            return [dx, dy]
        return [0, 0]

    def man(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0:
            a = -a
        b = y1 - y2
        if b < 0:
            b = -b
        return a + b

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = -10**18
    best_t = None

    for rx, ry in res:
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        score = (od - sd) * 100 - sd
        if best_t is None or score > best_score or (score == best_score and (rx, ry) < best_t):
            best_score = score
            best_t = (rx, ry)

    rx, ry = best_t
    # Choose move that maximizes (opponent advantage) and (resource closeness), avoiding obstacles.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        nsd = man(nx, ny, rx, ry)
        nod = man(ox, oy, rx, ry)
        score = (nod - nsd) * 100 - nsd
        if score > best_score + 0:
            best_score = score
            best = (dx, dy)
        elif score == best_score and best is not None:
            if (dx, dy) < best:
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]