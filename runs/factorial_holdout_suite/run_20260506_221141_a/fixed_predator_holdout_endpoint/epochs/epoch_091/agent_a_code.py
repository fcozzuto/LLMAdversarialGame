def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obstacles.add((x, y))

    res = []
    for r in observation.get("resources") or []:
        x, y = int(r[0]), int(r[1])
        if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
            res.append((x, y))

    if not res:
        return [0, 0]

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    moves = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = None
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h): 
            continue
        if (nx, ny) in obstacles:
            continue
        # Evaluate: best resource target where we are closer than opponent.
        cur_best = -10**9
        for rx, ry in res:
            sd = md(nx, ny, rx, ry)
            od = md(ox, oy, rx, ry)
            # Prefer being closer and reducing our distance; also move away from opponent if similar.
            sc = (od - sd) * 1000 - sd * 3 + (sd == od) * -5
            if sc > cur_best:
                cur_best = sc
        # Deterministic tie-break: prefer not staying still, then lexicographic (dx,dy).
        if best_score is None or cur_best > best_score or (cur_best == best_score and (dx, dy) < best):
            best_score = cur_best
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]