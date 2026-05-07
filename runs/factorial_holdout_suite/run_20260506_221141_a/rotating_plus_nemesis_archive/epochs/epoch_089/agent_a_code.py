def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_score = -10**18
    for rx, ry in resources:
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Favor resources we can reach earlier; if contested, prefer ones that are "safer" (we still closer or tie favors lower ds).
        score = (do - ds) * 100 - ds
        # Deterministic small bias to break ties: prefer lower y then lower x.
        score -= ry * 0.01 + rx * 0.001
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    # If no resources, move away from opponent while staying in bounds.
    if best_target is None:
        tx, ty = ox, oy
        best_move = [0, 0]
        best_val = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = man(nx, ny, tx, ty)
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
        return best_move

    tx, ty = best_target

    # Choose move that reduces distance to target and keeps us from stepping into obstacles.
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds_new = man(nx, ny, tx, ty)
        ds_old = man(sx, sy, tx, ty)
        # If we can reach sooner than opponent, prioritize that; otherwise, still reduce our distance and slightly avoid blocking.
        do = man(ox, oy, tx, ty)
        val = 0
        val += (do - ds_new) * 120
        val += (ds_old - ds_new) * 20
        val -= (nx - tx) * 0.001 + (ny - ty) * 0.002
        # Slight preference for stable progress (avoid staying unless best).
        if dx == 0 and dy == 0:
            val -= 0.5
        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move