def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    # Target resource where we are (most) ahead vs opponent; tie-break by being closer.
    best = None
    best_score = None
    for tx, ty in res:
        ds = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        score = (ds - do, ds, tx + ty)  # lexicographic; smaller is better
        if best_score is None or score < best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    best_move = None
    best_mscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        m1 = cheb(nx, ny, tx, ty)
        # If tie, prefer moves that also keep us not too close to opponent (reduce collision risk).
        m2 = cheb(nx, ny, ox, oy)
        mscore = (m1, m2, dx, dy)
        if best_mscore is None or mscore < best_mscore:
            best_mscore = mscore
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]