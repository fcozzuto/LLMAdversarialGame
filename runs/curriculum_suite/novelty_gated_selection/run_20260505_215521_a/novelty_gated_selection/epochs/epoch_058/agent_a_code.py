def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    best = (0, 0)
    best_score = -10**18
    selfd = cheb((sx, sy), (ox, oy))

    target = None
    if res:
        # nearest resource; tie-break by x then y for determinism
        target = min(res, key=lambda t: (cheb((sx, sy), t), t[0], t[1]))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        oppd = cheb((nx, ny), (ox, oy))
        if target is None:
            # chase opponent slightly
            score = -cheb((nx, ny), (ox, oy)) + 0.01 * oppd
        else:
            score = -cheb((nx, ny), target) + 0.001 * oppd
        # small preference for not staying if equally good
        if (dx, dy) != (0, 0) and score == best_score:
            score += 1e-9
        if score > best_score:
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]