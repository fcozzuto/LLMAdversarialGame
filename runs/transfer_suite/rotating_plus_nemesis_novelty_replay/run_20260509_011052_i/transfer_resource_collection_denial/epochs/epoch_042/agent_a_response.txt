def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in (observation.get("resources", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = -10**18
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # Prefer winning resources: higher margin = do-ds.
        # Also prefer lower absolute distance to finish sooner.
        val = (do - ds) * 100 - ds
        # If opponent is very close, strongly discourage.
        if do <= ds:
            val -= 50 * (ds - do + 1)
        if val > best_val:
            best_val = val
            best = (x, y)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # Candidate moves in prioritized order toward target (then small detours), deterministic.
    candidates = []
    candidates.append((dx, dy))
    candidates.append((dx, 0))
    candidates.append((0, dy))
    candidates.append((-dx, dy))
    candidates.append((dx, -dy))
    candidates.append((-dx, 0))
    candidates.append((0, -dy))
    candidates.append((0, 0))

    def ok(ncx, ncy):
        return 0 <= ncx < w and 0 <= ncy < h and (ncx, ncy) not in blocked

    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            # Ensure we don't "walk away" too much if target is still reachable.
            if (mx != 0 or my != 0) or len(resources) == 1:
                return [int(mx), int(my)]

    return [0, 0]