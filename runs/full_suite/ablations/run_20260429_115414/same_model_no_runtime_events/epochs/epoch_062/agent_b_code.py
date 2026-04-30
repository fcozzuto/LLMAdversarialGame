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

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def neighbor_free_count(x, y):
        c = 0
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if valid(nx, ny):
                c += 1
        return c

    if resources:
        # Pick best reachable-now resource: prefer where we are at least as close as opponent, then maximize lead.
        best_r = None
        best_key = None
        for rx, ry in resources:
            d1 = cheb(sx, sy, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # key: first prefer we are not worse; then smallest our dist; then largest lead
            not_worse = 0 if d1 <= d2 else 1
            key = (not_worse, d1, -(d2 - d1))
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        # No resources known: move toward center to keep options.
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_val = -10**18
    cur_to_opp = cheb(sx, sy, ox, oy)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        to_t = cheb(nx, ny, tx, ty)
        from_opp = cheb(nx, ny, ox, oy)
        progress = -to_t
        dist_gain = from_opp - cur_to_opp

        nf = neighbor_free_count(nx, ny)
        # Penalize squeezing into low-mobility cells.
        mobility = nf - 5  # roughly centered around 0

        # Small deterministic tie-break to avoid oscillation: prefer fewer steps from opponent? invert.
        key_tiebreak = -(from_opp + cheb(nx, ny, tx, ty) * 0.001)

        val = progress * 10 + dist_gain * 2 + mobility * 1 + int(key_tiebreak * 1000)
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]