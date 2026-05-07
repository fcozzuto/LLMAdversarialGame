def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))
        except Exception:
            pass

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))
        except Exception:
            pass

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obst:
            continue
        if res:
            dmin = min(man(nx, ny, rx, ry) for rx, ry in res)
            d_op = man(nx, ny, ox, oy)
            score = (-dmin * 1000) + (d_op)
        else:
            score = man(nx, ny, ox, oy)  # just drift away if no resources known
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]