def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for o in observation.get("obstacles") or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role") or "").lower()
    evade = ("evader" in role) or ("runner" in role) or ("evasive" in role) or ("evasion" in role)

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                res.append((x, y))
        elif isinstance(r, dict):
            x = r.get("x", None)
            y = r.get("y", None)
            if x is not None and y is not None:
                x, y = int(x), int(y)
                if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                    res.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    target = None
    if res:
        best = None
        bestd = 10**9
        for x, y in res:
            d = man(sx, sy, x, y)
            if d < bestd or (d == bestd and (x, y) < best):
                bestd = d
                best = (x, y)
        target = best

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target is not None:
            sc = -man(nx, ny, target[0], target[1])
            sc += 0.01 * (man(nx, ny, ox, oy) if evade else -man(nx, ny, ox, oy))
        else:
            sc = (man(nx, ny, ox, oy) if evade else -man(nx, ny, ox, oy))
        sc -= 1e-6 * (abs(dx) + abs(dy))
        if sc > best_score or (sc == best_score and (dx, dy) < tuple(best_move)):
            best_score = sc
            best_move = [dx, dy]

    return best_move