def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    ob = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x, y, a, b):
        return abs(x - a) + abs(y - b)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_moves = []
    cur = (sx, sy)

    resources = observation.get("resources") or []
    res_targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) not in ob and in_bounds(rx, ry):
                res_targets.append((rx, ry))
    target = (ox, oy) if not res_targets else min(res_targets, key=lambda t: dist(sx, sy, t[0], t[1]))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if in_bounds(nx, ny) and (nx, ny) not in ob:
            best_moves.append((nx, ny, dx, dy))
    if not best_moves:
        return [0, 0]

    # primary: move toward target; secondary: stay away from opponent if we have no resources
    towards = dist
    scored = []
    for nx, ny, dx, dy in best_moves:
        d_t = towards(nx, ny, target[0], target[1])
        d_o = towards(nx, ny, ox, oy)
        edge = min(nx, w - 1 - nx, ny, h - 1 - ny)
        if not res_targets:
            score = (d_t, -d_o, -edge, dx, dy)
        else:
            score = (d_t, d_o, -edge, dx, dy)
        scored.append((score, dx, dy))
    scored.sort(key=lambda z: z[0])
    return [int(scored[0][1]), int(scored[0][2])]