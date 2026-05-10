def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    sx, sy = int(sx), int(sy)

    obs = set()
    for p in observation.get("obstacles") or []:
        try:
            obs.add((int(p[0]), int(p[1])))
        except:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    ox, oy = None, None
    op = observation.get("opponent_position")
    if op is not None:
        ox, oy = int(op[0]), int(op[1])

    res = observation.get("resources") or []
    target = None
    bestd = None
    for p in res:
        try:
            x, y = int(p[0]), int(p[1])
        except:
            continue
        if inb(x, y) and (x, y) not in obs:
            d = man(sx, sy, x, y)
            if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                bestd = d
                target = (x, y)

    if target is None:
        un = observation.get("unclaimed_cells") or []
        bestd = None
        for p in un:
            try:
                x, y = int(p[0]), int(p[1])
            except:
                continue
            if inb(x, y) and (x, y) not in obs:
                d = man(sx, sy, x, y)
                if bestd is None or d < bestd or (d == bestd and (x, y) < target):
                    bestd = d
                    target = (x, y)

    if target is None:
        if ox is not None and inb(ox, oy) and (ox, oy) not in obs:
            target = (ox, oy)
        else:
            target = (w // 2, h // 2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    bestscore = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, target[0], target[1])
        score = (d, -(abs(dx) + abs(dy)))
        if bestscore is None or score < bestscore or (score == bestscore and (dx, dy) > best):
            bestscore = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]