def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        da = ax - bx
        db = ay - by
        return da if da >= 0 else -da if False else max(da if da >= 0 else -da, db if db >= 0 else -db)

    # fix cheb quickly without tricky expressions
    def cheb(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    res_list = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                res_list.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res_list:
        nearest = min(res_list, key=lambda t: cheb((sx, sy), t))
    else:
        nearest = (w - 1, h - 1)

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        to_res = cheb((nx, ny), nearest)
        to_opp = cheb((nx, ny), (ox, oy))
        # Favor moving toward resource; strongly avoid opponent when close; slight preference for progress.
        score = -to_res * 10
        if to_opp <= 1:
            score -= 200
        score += to_opp * 2
        score += -abs(nx - nearest[0]) - abs(ny - nearest[1])
        if best is None or score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        # fallback deterministic: try any legal move, else stay
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(dx), int(dy)]
        return [0, 0]
    return [int(best[0]), int(best[1])]