def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    # Evaluate each possible next position by how much it improves our "lead" on resources.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy

        lead = 0
        # Prefer resources we can reach sooner or tie, but also consider closeness if tied.
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not (isinstance(tx, int) and isinstance(ty, int)):
                continue
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            # Winning resource gives large positive, losing gives negative, exact tie gives small preference.
            if ds < do:
                v = 6 - ds + 0.1 * (do - ds)
            elif ds == do:
                v = 1.0 - 0.05 * ds
            else:
                v = - (ds - do) - 0.02 * ds
            # Also mildly reward moving toward resources that are closer in absolute distance.
            v += 0.01 * (8 - ds) - 0.001 * (8 - do)
            if v > lead:
                lead = v

        # Secondary tie-break: minimize our distance to the best resource.
        best_ds = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            if not (isinstance(tx, int) and isinstance(ty, int)):
                continue
            ds = cheb(nx, ny, tx, ty)
            if best_ds is None or ds < best_ds:
                best_ds = ds

        key = (lead, -(best_ds if best_ds is not None else 10))
        if best_val is None or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]