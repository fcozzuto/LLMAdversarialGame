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
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def score_cell(rx, ry):
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        lead = od - sd  # positive if we arrive sooner
        # Prefer closer cells when lead ties; also avoid near-opponent so we don't walk into their denial path.
        opp_dist = cheb(ox, oy, rx, ry)
        return (lead * 1000) - (sd * 10) + (opp_dist)

    target = None
    best = None
    for rx, ry in resources:
        sc = score_cell(rx, ry)
        if best is None or sc > best:
            best = sc
            target = (rx, ry)

    if target is None:
        return [0, 0]
    tx, ty = target

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue
        d = cheb(nx, ny, tx, ty)
        # If multiple, prefer blocking opponent slightly by moving to reduce their cheb distance.
        od = cheb(ox, oy, tx, ty)  # opponent target distance baseline
        m_sc = (-d * 100) + (od - cheb(ox, oy, tx, ty)) + (1 if (nx, ny) == (tx, ty) else 0)
        if best_m_sc is None or m_sc > best_m_sc:
            best_m_sc = m_sc
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]