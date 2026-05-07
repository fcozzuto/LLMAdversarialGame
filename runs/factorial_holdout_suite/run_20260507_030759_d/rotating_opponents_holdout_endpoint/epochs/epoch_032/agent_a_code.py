def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    target = None
    best = None
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources we can reach sooner, and that are "safer" vs opponent proximity.
        score = (od - sd) * 100 - sd
        if best is None or score > best or (score == best and (x, y) < target):
            best = score
            target = (x, y)

    tx, ty = target
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                candidates.append((dx, dy))
    if not candidates:
        return [0, 0]

    # Greedily move to minimize our distance to target, with deterministic tie-break.
    best_move = None
    best_d = None
    for dx, dy in sorted(candidates):
        nx, ny = sx + dx, sy + dy
        d = cheb(nx, ny, tx, ty)
        # Small anti-denial: also avoid giving opponent a much closer approach this turn.
        n_opp = cheb(ox, oy, tx, ty)
        metric = (d, -n_opp)
        if best_move is None or metric < best_d:
            best_d = metric
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]