def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def md(ax, ay, bx, by): return abs(ax - bx) + abs(ay - by)

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if legal(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2 and legal(p[0], p[1]):
                rpos.append((p[0], p[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y):
                rpos.append((x, y))

    if not rpos:
        return [0, 0]

    # Choose a resource where we are closer than opponent; otherwise pick best achievable advantage.
    best_t = None
    best_val = -10**9
    for tx, ty in rpos:
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        if ds == 0:
            return [0, 0]
        # Advantage: larger when we are closer; tie-break by smaller opponent distance and then smaller ds.
        val = (do - ds) * 10 - do - ds
        if val > best_val:
            best_val = val
            best_t = (tx, ty)

    tx, ty = best_t
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    curr_ds = md(sx, sy, tx, ty)

    def obstacle_pressure(x, y):
        # Prefer cells with more free neighbors to avoid getting stuck against obstacles.
        free = 0
        for dx, dy in dirs:
            if (dx, dy) == (0, 0):
                continue
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                free += 1
        return free

    best_move = [0, 0]
    best_score = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nds = md(nx, ny, tx, ty)
        # Strongly prefer improving distance; if stuck, choose the most mobile option.
        improve = nds - curr_ds
        # Also lightly bias away from giving opponent a direct closer chase.
        ndo = md(ox, oy, nx, ny)
        score = (0 if improve < 0 else 50) + nds * 2 - obstacle_pressure(nx, ny) - ndo * 0.05
        if score < best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move