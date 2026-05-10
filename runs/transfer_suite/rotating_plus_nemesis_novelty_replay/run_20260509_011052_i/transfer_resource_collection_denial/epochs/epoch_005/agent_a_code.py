def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def cell_blocked(x, y):
        return (x, y) in obs

    if resources:
        best_t = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            # Prefer we arrive no later; otherwise still prefer larger lead over opponent.
            lead = od - sd
            # Deterministic tie-break by fixed hash.
            tie = (rx * 131 + ry * 17) % 997
            key = (-lead, sd, tie)  # smaller is better
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = w // 2, h // 2

    # If target is blocked (rare), switch to nearest unblocked resource.
    if cell_blocked(tx, ty) and resources:
        best_t = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if cell_blocked(rx, ry):
                continue
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - sd
            tie = (rx * 131 + ry * 17) % 997
            key = (-lead, sd, tie)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (rx, ry)
        tx, ty = best_t if best_t is not None else (w // 2, h // 2)

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or cell_blocked(nx, ny):
            continue
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # Main objective: improve relative capture pressure on target.
        rel = (od - sd)
        # Secondary: move closer to target; tertiary: avoid stepping away.
        val = (-rel, sd, (nx * 131 + ny * 17) % 997)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]