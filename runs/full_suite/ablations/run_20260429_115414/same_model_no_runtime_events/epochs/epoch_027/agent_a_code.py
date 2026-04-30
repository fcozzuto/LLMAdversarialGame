def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(tx, ty, sdist, odist):
        # Prefer taking resources we can beat opponent on (odist - sdist > 0),
        # then faster, then closer to center-ish tie-break.
        cen_x, cen_y = (w - 1) / 2.0, (h - 1) / 2.0
        center_pen = abs(tx - cen_x) + abs(ty - cen_y)
        lead = odist - sdist
        return (lead, -sdist, -(odist), -center_pen, -tx, -ty)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0: nx = sx
        if nx >= w: nx = sx
        if ny < 0: ny = sy
        if ny >= h: ny = sy
        # Engine will enforce invalid moves; this keeps us in bounds for scoring.
        s_best = None
        for rx, ry in resources:
            sdist = cheb(nx, ny, rx, ry)
            odist = cheb(ox, oy, rx, ry)
            if s_best is None:
                s_best = best_target(rx, ry, sdist, odist) + (rx, ry)
            else:
                cand = best_target(rx, ry, sdist, odist) + (rx, ry)
                if cand > s_best:
                    s_best = cand
        # Score movement by best target alignment; tie-break by resulting coords.
        # Also add a small term to prefer reducing our nearest resource distance overall.
        if s_best is None:
            continue
        nearest_s = min(cheb(nx, ny, rx, ry) for (rx, ry) in resources)
        val = (s_best[0], s_best[1], s_best[2], -nearest_s, -nx, -ny, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]