def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1)]
    best_move = (0, 0)
    best_val = -10**9
    best_min_dist = 10**9

    # If no resources, move to maximize distance from opponent corner and toward center a bit.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            opp_d = cheb(nx, ny, ox, oy)
            cen_d = cheb(nx, ny, cx, cy)
            val = opp_d - 0.2 * cen_d
            if val > best_val:
                best_val = val
                best_min_dist = 10**9
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Compete: maximize (opponent distance - our distance) to whichever resource yields best margin.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        min_our = 10**9
        best_margin = -10**9
        for rx, ry in resources:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            if our_d < min_our:
                min_our = our_d
            margin = opp_d - our_d
            if margin > best_margin:
                best_margin = margin
        # Prefer higher margin; if tied, prefer smaller our distance.
        val = best_margin * 1000 - min_our
        if val > best_val:
            best_val = val
            best_min_dist = min_our
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]