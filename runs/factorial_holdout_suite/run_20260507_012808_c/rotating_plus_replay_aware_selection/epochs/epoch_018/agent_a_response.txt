def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            val = cheb(ox, oy, nx, ny) - cheb(sx, sy, nx, ny) - cheb(nx, ny, cx, cy) * 0.1
            if best is None or val > best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    opp_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = ox + dx, oy + dy
            if ok(nx, ny):
                opp_moves.append((dx, dy))

    best = None
    rem = observation.get("remaining_resource_count", len(resources))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        our_best = None
        for rx, ry in resources:
            od = cheb(nx, ny, rx, ry)
            # assume opponent will greedily minimize their distance to this same resource
            opp_best = None
            for oxdx, oydy in opp_moves:
                onx, ony = ox + oxdx, oy + oydy
                d = cheb(onx, ony, rx, ry)
                if opp_best is None or d < opp_best:
                    opp_best = d
            # margin: larger is better; slight tie-break toward closer overall
            margin = (opp_best - od) + (0.02 * (12 - rem))
            if our_best is None or margin > our_best:
                our_best = margin
        val = our_best
        if best is None or val > best[0]:
            best = (val, dx, dy)

    return [best[1], best[2]]