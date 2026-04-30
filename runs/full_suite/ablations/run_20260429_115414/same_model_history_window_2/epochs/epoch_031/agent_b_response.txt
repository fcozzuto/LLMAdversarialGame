def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in blocked

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    rem = observation.get("remaining_resource_count", 0)
    try:
        rem = int(rem)
    except:
        rem = len(resources)

    if rem <= 0 or not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = cheb(nx, ny, cx, cy)
            if val < best[0]:
                best = (val, (dx, dy))
        return [best[1][0], best[1][1]]

    best_t = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(sx, sy, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        key = (d1 - 0.75 * d2, d1, d2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    rx, ry = best_t
    best_move = (0, 0)
    best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = cheb(nx, ny, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer reducing distance to our chosen target while not letting opponent be too close.
        # Also add slight preference for moving toward the other best resources if we're tied.
        val = d_self - 0.65 * d_opp
        if dx == 0 and dy == 0:
            val += 0.05
        if val < best_val:
            best_val = val
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]