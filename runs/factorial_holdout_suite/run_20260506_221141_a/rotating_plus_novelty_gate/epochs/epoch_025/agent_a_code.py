def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, dict):
            x, y = p.get("x", None), p.get("y", None)
            if x is not None and y is not None:
                x, y = int(x), int(y)
            else:
                continue
        else:
            if not p or len(p) < 2:
                continue
            x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            x, y = r.get("x", None), r.get("y", None)
            if x is None or y is None:
                pos = r.get("position", None)
                if pos and len(pos) >= 2:
                    x, y = pos[0], pos[1]
                else:
                    continue
        else:
            if not r or len(r) < 2:
                continue
            x, y = r[0], r[1]
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
            res.append((x, y))
    if not res:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a resource that favors self (closer) and discourages opponent (not too close for them).
    best = None
    best_key = None
    for (rx, ry) in res:
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = None
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue
        ns = dist((nx, ny), (tx, ty))
        no = dist((nx, ny), (ox, oy))
        score = (ns, -no, abs(dx) + abs(dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]