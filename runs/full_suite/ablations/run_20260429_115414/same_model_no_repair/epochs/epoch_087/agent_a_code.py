def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Choose the resource that we can reach first (or, if none, the one with least negative advantage),
    # then pick the move that maximizes our advantage from that resource.
    best_move = (0, 0)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obs:
            continue

        best_margin = None
        best_myd = None
        best_opd = None

        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            margin = opd - myd  # positive => we are closer to that resource
            if best_margin is None:
                best_margin, best_myd, best_opd = margin, myd, opd
            else:
                if margin > best_margin or (margin == best_margin and myd < best_myd) or (margin == best_margin and myd == best_myd and opd < best_opd):
                    best_margin, best_myd, best_opd = margin, myd, opd

        if best_margin is None:
            continue

        # Tie-break: prefer moves that also make the opponent farther from the same target.
        key = (best_margin, -best_myd, best_opd)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]