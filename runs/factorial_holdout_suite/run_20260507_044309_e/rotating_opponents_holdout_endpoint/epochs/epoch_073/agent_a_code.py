def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def move_ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target resource, prioritizing grabbing leads but correcting for small-distance ties.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        if ds == 0:
            best = (rx, ry)
            best_key = (10**9, -0, 0, rx, ry)
            break
        lead = do - ds  # positive means we are closer (or more quickly reaching)
        key = (lead, -ds, -(rx + ry), (rx * 31 + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Choose move that maximizes our progress and reduces opponent's relative lead.
    best_m = None
    best_m_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not move_ok(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(ox, oy, tx, ty)
        # Also encourage moving toward a resource that is not worse for us if we can't reach instantly.
        lead_after = no - ns
        self_step = cheb(sx, sy, tx, ty) - ns
        key = (lead_after, self_step, -ns, -(nx + 2 * ny), dx * dx + dy * dy)
        if best_m_key is None or key > best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]