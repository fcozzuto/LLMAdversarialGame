def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        margin = do - ds  # positive means we are closer
        # Prefer contested wins; tie-break toward smaller self distance and more "ahead" positions deterministically.
        key = (margin, -ds, -(rx + 2 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose move that best reduces our distance to target, but avoid stepping onto obstacles/out of bounds.
    best_m = [0, 0]
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue
        nds = cd(nx, ny, tx, ty)
        ndo = cd(nx, ny, ox, oy)
        # Secondary: slightly keep away from opponent to avoid them stealing tempo.
        mkey = (-nds, ndo, dx, dy)
        if best_m_key is None or mkey > best_m_key:
            best_m_key = mkey
            best_m = [dx, dy]

    return best_m