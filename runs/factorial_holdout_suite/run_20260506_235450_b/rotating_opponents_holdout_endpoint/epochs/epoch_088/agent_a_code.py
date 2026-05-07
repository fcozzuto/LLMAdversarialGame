def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for ob in obstacles:
        if isinstance(ob, (list, tuple)) and len(ob) >= 2:
            x, y = int(ob[0]), int(ob[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    # Pick best target: prioritize resources we can arrive no later than opponent; then closer; then deterministic tie-break.
    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = int(r[0]), int(r[1])
        if not inb(tx, ty) or (tx, ty) in obs:
            continue
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        key = (od - sd, -(sd + od), -min(sd, od), -(tx + 31 * ty), tx, ty)
        if best is None or key > best[0]:
            best = (key, tx, ty)

    if best is None:
        # No reachable resource: drift to safer corner away from opponent line, deterministic.
        dx = -1 if ox > sx else (1 if ox < sx else 0)
        dy = -1 if oy > sy else (1 if oy < sy else 0)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        return [0, 0]

    _, tx, ty = best

    # Choose a single-step move toward target, avoiding obstacles/bounds, deterministic tie-break.
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    bestm = None  # (dist, -capture_bias, dx, dy, nx, ny)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = man(nx, ny, tx, ty)
        # If stepping onto target, strongly prefer it.
        capture_bias = 1 if (nx == tx and ny == ty) else 0
        key = (d, -capture_bias, dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]