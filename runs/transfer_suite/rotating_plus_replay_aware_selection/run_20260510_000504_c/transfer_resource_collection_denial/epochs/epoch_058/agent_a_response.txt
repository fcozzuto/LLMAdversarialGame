def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
        elif isinstance(p, dict):
            q = p.get("position", p)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                obstacles.add((int(q[0]), int(q[1])))
            elif "x" in p and "y" in p:
                obstacles.add((int(p["x"]), int(p["y"])))
    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            q = r.get("position", r)
            if isinstance(q, (list, tuple)) and len(q) >= 2:
                resources.append((int(q[0]), int(q[1])))
            elif "x" in r and "y" in r:
                resources.append((int(r["x"]), int(r["y"])))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def best_target():
        best = None
        for rx, ry in resources:
            myd = step_dist(sx, sy, rx, ry)
            opd = step_dist(ox, oy, rx, ry)
            score = myd - 1.05 * opd  # prefer resources closer than opponent
            if best is None or score < best[0]:
                best = (score, rx, ry, myd, opd)
        return best[1], best[2]

    tx, ty = best_target()

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            if (nx, ny) in obstacles:
                continue
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def eval_move(dx, dy, nx, ny):
        myd = step_dist(nx, ny, tx, ty)
        # lightly repel moving into a cell the opponent is much closer to
        oppd = step_dist(ox, oy, nx, ny)
        # avoid stepping "away" from target
        toward = (step_dist(sx, sy, tx, ty) - myd)
        return myd - 0.12 * oppd - 0.35 * toward

    best = None
    for dx, dy, nx, ny in moves:
        val = eval_move(dx, dy, nx, ny)
        if best is None or val < best[0] or (val == best[0] and (dx, dy) < best[1]):
            best = (val, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]