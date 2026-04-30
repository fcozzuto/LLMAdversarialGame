def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Choose target: prefer resources where we are strictly closer than opponent.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # key: maximize advantage, then minimize my distance, then coordinates for determinism
            adv = opd - myd
            key = (-(adv), myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)

        tx, ty = best
    else:
        tx, ty = (w // 2, h // 2)

    # If opponent is closer to the chosen target by 2+, try to intercept nearer to us.
    if resources:
        opd = cheb(ox, oy, tx, ty)
        myd = cheb(sx, sy, tx, ty)
        if opd - myd >= 2:
            # pick a resource closest to opponent but also closer to us than to their position
            best2 = None
            best2_key = None
            for rx, ry in resources:
                myd2 = cheb(sx, sy, rx, ry)
                opd2 = cheb(ox, oy, rx, ry)
                if myd2 <= myd and myd2 < opd2:
                    # deny: prefer those opponent would take soon (small opd2)
                    key = (opd2, myd2, rx, ry)
                    if best2_key is None or key < best2_key:
                        best2_key = key
                        best2 = (rx, ry)
            if best2 is not None:
                tx, ty = best2

    # Move: minimize resulting distance to target; tie-break by moving away from opponent.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_t = cheb(nx, ny, tx, ty)
        d_opp = cheb(nx, ny, ox, oy)
        # Prefer smaller d_to_t; then larger d_opp (reduce contest chance); then deterministic
        key = (d_to_t, -d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]