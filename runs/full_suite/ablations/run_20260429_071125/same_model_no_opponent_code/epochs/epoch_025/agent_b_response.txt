def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if (sx, sy) in resources:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            moves.append((dx, dy))

    target = None
    best = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; break ties by our distance, then position.
        score = (do - ds, -ds, -rx, -ry)
        if best is None or score > best:
            best = score
            target = (rx, ry)

    if target is None:
        # No visible resources: move toward board center while staying collision-safe
        cx, cy = (w - 1) // 2, (h - 1) // 2
        target = (cx, cy)

    tx, ty = target
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        d_self = cd(nx, ny, tx, ty)
        d_opp = cd(nx, ny, ox, oy)
        # Primary: closer to target; secondary: farther from opponent; tertiary: deterministic tie-break.
        val = (-d_self, d_opp, -dx, -dy, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if not inside(sx, sy):
        # Shouldn't happen; fallback to staying if somehow blocked.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]