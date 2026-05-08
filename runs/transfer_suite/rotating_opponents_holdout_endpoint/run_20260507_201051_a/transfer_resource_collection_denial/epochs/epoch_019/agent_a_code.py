def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
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

    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        reach_adv = do - ds
        # Prefer winning first, then closer to self, then higher coordinate determinism
        key = (reach_adv, -ds, -man(ox, oy, rx, ry), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        # fallback: move toward any in-bounds, non-obstacle cell
        return [0, 0]

    (tx, ty) = best[1]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_step = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        nds = man(nx, ny, tx, ty)
        ndio = man(nx, ny, ox, oy)
        # prioritize decreasing distance to target; if tie, prefer reducing opponent distance a bit deterministically
        key = (-nds, -ndio, dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best_step = (dx, dy)

    if best_step is None:
        return [0, 0]
    return [int(best_step[0]), int(best_step[1])]