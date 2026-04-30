def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d1 = dist(nx, ny, cx, cy)
            d2 = dist(nx, ny, ox, oy)
            key = (d1, d2, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Target where we are most likely to arrive first (chebyshev distance)
    best_t = None
    for tx, ty in resources:
        ds = dist(sx, sy, tx, ty)
        do = dist(ox, oy, tx, ty)
        # prioritize (do - ds), then smaller ds, then lexical tie-break
        key = (-(do - ds), ds, tx, ty)
        if best_t is None or key < best_t[0]:
            best_t = (key, tx, ty)
    tx, ty = best_t[1], best_t[2]

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = dist(nx, ny, tx, ty)
        do_next = dist(ox, oy, tx, ty)
        # maximize relative advantage; if tie, minimize remaining distance to target; then reduce closeness to opponent
        adv = do_next - ds_next
        d_opp = dist(nx, ny, ox, oy)
        key = (-adv, ds_next, d_opp, dx, dy)
        if best is None or key < best[0]:
            best = (key, dx, dy)
    return [best[1], best[2]]