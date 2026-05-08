def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    if isinstance(sp, dict):
        sp = sp.get("position", sp.get("pos", [0, 0]))
    if isinstance(op, dict):
        op = op.get("position", op.get("pos", [0, 0]))
    sx, sy = (int(sp[0]), int(sp[1])) if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = (int(op[0]), int(op[1])) if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for o in obstacles:
        if isinstance(o, dict):
            o = o.get("position", o.get("pos", None))
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, dict):
            r = r.get("position", r.get("pos", None))
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    if not res:
        return [0, 0]

    target = res[0]
    bestd = cheb((sx, sy), target)
    for r in res[1:]:
        d = cheb((sx, sy), r)
        if d < bestd:
            bestd = d
            target = r

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        d = cheb((nx, ny), target)
        score = -d
        if dx == 0 and dy == 0:
            score -= 0.1
        if (nx, ny) == target:
            score += 1000
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]