def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for o in (observation.get("obstacles", []) or []):
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res:
        return [0, 0]

    def man(a, b, x, y):
        return abs(x - a) + abs(y - b)

    def base_score(rx, ry):
        self_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        aligned = 1 if (rx == ox or ry == oy) else 0  # vs sweep-rows style
        return (opp_d - self_d) - 0.75 * aligned

    def obs_risk(x, y):
        if (x, y) in obstacles:
            return 10**9
        p = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (x + dx, y + dy) in obstacles:
                    p += 1
        return p

    def best_from(x, y):
        best = -10**18
        for rx, ry in res:
            self_d = man(x, y, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            aligned = 1 if (rx == ox or ry == oy) else 0
            s = (opp_d - self_d) - 0.75 * aligned
            if s > best:
                best = s
        return best

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        v = best_from(nx, ny) - 2.0 * obs_risk(nx, ny)
        if v > best_val:
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]