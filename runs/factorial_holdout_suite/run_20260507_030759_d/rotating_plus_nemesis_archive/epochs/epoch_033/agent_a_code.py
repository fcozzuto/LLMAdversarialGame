def choose_move(observation):
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
        except Exception:
            pass

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_score = None

    if res:
        target = None
        best_d = None
        for rx, ry in res:
            d = man(sx, sy, rx, ry)
            if best_d is None or d < best_d or (d == best_d and (rx, ry) < target):
                best_d = d
                target = (rx, ry)
        tx, ty = target
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            ds = man(nx, ny, tx, ty)
            do = man(nx, ny, ox, oy)
            score = (-ds, do)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]
    else:
        # No resources: maximize distance from opponent (and avoid obstacles)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obst:
                continue
            score = (man(nx, ny, ox, oy), -abs(dx) - abs(dy))
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]