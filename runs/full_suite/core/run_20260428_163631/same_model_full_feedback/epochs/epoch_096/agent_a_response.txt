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
    obstacles.discard((sx, sy))
    obstacles.discard((ox, oy))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]
    if (sx, sy) in set(resources):
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    center = (w - 1) / 2.0, (h - 1) / 2.0
    opp_c = cheb(ox, oy, center[0], center[1])

    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        lead = do - ds  # positive if we are closer
        # Prefer guaranteed leads, then shorter own distance, then farther from opponent, then lexicographic
        key = (lead, -ds, do, -(cheb(ox, oy, rx, ry)), -abs(rx - center[0]) - abs(ry - center[1]), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if (nx, ny) == (sx, sy) or cheb(nx, ny, tx, ty) <= cheb(sx, sy, tx, ty) + 1:
            d = cheb(nx, ny, tx, ty)
            # Also discourage moving into cells closer to opponent than our current lead (lightly)
            do_next = cheb(ox, oy, nx, ny)
            our_lead_now = cheb(ox, oy, tx, ty) - cheb(sx, sy, tx, ty)
            our_lead_next = cheb(ox, oy, tx, ty) - d
            key = (our_lead_next, -d, -our_lead_now, -(do_next), -abs(nx - center[0]) - abs(ny - center[1]), dx, dy)
            if best_m_key is None or key > best_m_key:
                best_m_key = key
                best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]