def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))

    if not res or (sx, sy) in set(res):
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_key = None
    for (rx, ry) in res:
        myd = md(rx, ry, sx, sy)
        opd = md(rx, ry, ox, oy)
        gain = opd - myd
        key = (gain, -myd, rx, ry)
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    nx, ny = sx + dx, sy + dy
    if (dx != 0 and dy != 0) and ((nx, sy) in obstacles or (sx, ny) in obstacles):
        if (nx, sy) not in obstacles:
            dy = 0
        elif (sx, ny) not in obstacles:
            dx = 0
        else:
            if (nx, ny) not in obstacles:
                dx, dy = dx, dy
            else:
                if (sx + dx, sy) in obstacles and (sx, sy + dy) in obstacles:
                    return [0, 0]
                if (sx + dx, sy) not in obstacles:
                    dy = 0
                else:
                    dx = 0
    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        options = []
        if (sx + dx, sy) not in obstacles and 0 <= sx + dx < w:
            options.append((dx, 0))
        if (sx, sy + dy) not in obstacles and 0 <= sy + dy < h:
            options.append((0, dy))
        if (dx, dy) != (0, 0) and (sx + dx, sy + dy) not in obstacles and 0 <= nx < w and 0 <= ny < h:
            options.append((dx, dy))
        if options:
            return list(sorted(options, key=lambda v: (-(md(sx + v[0], sy + v[1], rx, ry)), v[0], v[1]))[0])
        return [0, 0]

    return [dx, dy]