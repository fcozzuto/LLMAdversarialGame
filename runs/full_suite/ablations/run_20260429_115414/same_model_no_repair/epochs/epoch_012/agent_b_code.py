def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources or rem <= 0:
        # Deterministic fallback: move toward corner closer to having shorter distance
        tx, ty = (w - 1, h - 1) if cheb(sx, sy, w - 1, h - 1) <= cheb(sx, sy, 0, 0) else (0, 0)
    else:
        best_score = None
        tx, ty = resources[0]
        # Score: prefer resources we can reach at least as fast as opponent, then reduce our distance;
        # small bias toward center to avoid corner-milling.
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            lead = opd - myd  # positive means we are closer
            center_bias = -((rx - (w - 1) / 2.0) ** 2 + (ry - (h - 1) / 2.0) ** 2) / (w + h)
            # If both can reach, push toward slightly earlier targets (smaller myd).
            score = (lead, -myd, center_bias, -rx, -ry)
            if best_score is None or score > best_score:
                best_score = score
                tx, ty = rx, ry

    # Greedy step toward target with deterministic tie-break; avoid obstacles.
    cx, cy = sx, sy
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        # Also consider opponent pressure at the next position.
        opd2 = cheb(ox, oy, tx, ty)
        lead2 = opd2 - myd2
        toward = -(myd2)
        # Encourage not moving away from both center and target.
        center = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) / (w + h)
        val = (lead2, toward, center, -abs(nx - tx) - abs(ny - ty), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]