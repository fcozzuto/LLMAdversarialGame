def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    if not resources:
        return [0, 0]

    # Pick a resource we can plausibly reach at least not later than opponent.
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer targets where we are closer; if tie, prefer larger margin for safety.
        score = (ds <= do, do - ds, -ds, -rx, -ry)
        if best is None or score > best[0]:
            best = (score, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    candidates = [(-1, -1), (0, -1), (1, -1),
                  (-1, 0), (0, 0), (1, 0),
                  (-1, 1), (0, 1), (1, 1)]

    bestm = (0, 0)
    bestv = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = man(nx, ny, tx, ty)
        # Estimate if we stay ahead: compare against opponent's fixed distance.
        do = man(ox, oy, tx, ty)
        # Also lightly bias toward reducing opponent reach by moving generally toward their likely contested area.
        margin = do - ds2
        # Penalize moves that increase distance to target.
        prog = man(sx, sy, tx, ty) - ds2
        # If we can take the resource sooner, prefer it; otherwise, maximize margin/progress.
        v = (ds2 <= do, margin, prog, -ds2, dx, dy)
        if bestv is None or v > bestv:
            bestv = v
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]