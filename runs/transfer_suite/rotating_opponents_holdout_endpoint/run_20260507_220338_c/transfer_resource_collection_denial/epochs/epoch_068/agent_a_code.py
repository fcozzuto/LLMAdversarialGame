def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    turns_remaining = observation.get("turns_remaining", 0)

    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))
    resset = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            resset.add((p[0], p[1]))

    if (sx, sy) in resset:
        return [0, 0]

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = None
    t = turns_remaining if isinstance(turns_remaining, int) else int(turns_remaining or 0)
    for rx, ry in resset:
        if (rx, ry) in obst:
            continue
        sd = man(sx, sy, rx, ry)
        od = man(ox, oy, rx, ry)
        # Prefer resources we can beat; add time pressure to commit.
        time_pressure = 1.0 + max(0, (8 * 8 - t) / (8 * 8))
        key = (od - sd, -sd * time_pressure, -(rx + 2 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move away from opponent if no resources found.
        dx = 0
        dy = 0
        if ox > sx: dx = -1
        elif ox < sx: dx = 1
        if oy > sy: dy = -1
        elif oy < sy: dy = 1
        return [dx, dy]

    tx, ty = best
    curd = man(sx, sy, tx, ty)
    best_move = [0, 0]
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        nd = man(nx, ny, tx, ty)
        # If we can tie/deny, prioritize moving into opponent competition radius.
        oppd = man(ox, oy, nx, ny)
        mkey = (-nd, -oppd, -((nx + 2 * ny) - (sx + 2 * sy)) if nd <= curd else 0, 1 if (nx, ny) == (tx, ty) else 0)
        if best_mkey is None or mkey > best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    return best_move