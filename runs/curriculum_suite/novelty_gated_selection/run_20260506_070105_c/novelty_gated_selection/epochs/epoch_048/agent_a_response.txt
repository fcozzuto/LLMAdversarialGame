def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set(tuple(o) for o in (observation.get("obstacles", []) or []))
    resources = [tuple(r) for r in (observation.get("resources", []) or []) if tuple(r) not in obstacles]
    if not resources:
        dx = 1 if ox > sx else (-1 if ox < sx else 0)
        dy = 1 if oy > sy else (-1 if oy < sy else 0)
        return [dx, dy]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def step_cost(x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return 0
        return max(abs(dx), abs(dy))  # king-move distance

    # Evaluate candidate next steps by how much they improve our access to resources
    # while keeping distance from opponent's potential access.
    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer moves that get us closer to the best "personal" resource
        # while not giving opponent a near alternative.
        cur_best = None
        for rx, ry in resources:
            myd = step_cost(nx, ny, rx, ry)
            opd = step_cost(ox, oy, rx, ry)
            # Score: prioritize smaller myd, larger opd; slight diagonal bias to break ties.
            diag = abs((rx - nx) - (ry - ny))
            v = (myd, -opd, diag)
            if cur_best is None or v < cur_best:
                cur_best = v
        myd, neg_opd, diag = cur_best

        # Also try to "shadow" opponent by moving away if we accidentally move closer
        # to the nearest opponent-resource.
        # (Cheap: estimate opponent best resource distance from our chosen next cell.)
        opp_near = 10**9
        for rx, ry in resources:
            opp_near = min(opp_near, step_cost(ox, oy, rx, ry) - step_cost(nx, ny, rx, ry))
        # Combine
        val = (myd, neg_opd, diag, opp_near)

        if best is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]