def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        try:
            obst.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick target resource by who gets it first, with distance penalty to avoid dithering.
    best_t = None
    best_sc = -10**18
    for r in resources:
        tx, ty = int(r[0]), int(r[1])
        ds = md(sx, sy, tx, ty)
        do = md(ox, oy, tx, ty)
        # Primary: maximize advantage in reaching time.
        adv = do - ds
        sc = adv * 1000 - ds * 3
        # Secondary: slightly prefer closer to reduce horizon risk.
        sc += -min(ds, 2) * 10
        if sc > best_sc:
            best_sc = sc
            best_t = (tx, ty)

    tx, ty = best_t

    # Choose move that maximizes advantage after the move; avoid obstacles when possible.
    best_mv = (0, 0)
    best_mv_sc = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obst:
            continue
        ns = md(nx, ny, tx, ty)
        no = md(ox, oy, tx, ty)
        # Advantage in taking the target next.
        sc = (no - ns) * 1000 - ns * 5
        # If we can potentially step onto a resource, boost.
        if [nx, ny] in resources:
            sc += 20000
        # Small tie-break to drift consistently toward target.
        cur = md(sx, sy, tx, ty)
        if ns < cur:
            sc += 50
        if sc > best_mv_sc:
            best_mv_sc = sc
            best_mv = (dx, dy)

    # If all moves blocked/invalid, stay.
    return [int(best_mv[0]), int(best_mv[1])]