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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (-10**18, 0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Choose best resource to contest from the next position.
        if resources:
            chosen = None
            chosen_key = None
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                adv = opd - myd
                key = (-adv, myd, rx, ry)  # maximize adv, then smaller myd
                if chosen_key is None or key < chosen_key:
                    chosen_key = key
                    chosen = (rx, ry, myd, opd, adv)
            rx, ry, myd, opd, adv = chosen
            score = adv * 1000 - myd * 2
            # If I'm not closer, slightly prefer moves that reduce my distance anyway.
            if adv < 0:
                score -= (-adv) * 200
        else:
            # No resources: move to keep pressure near opponent and center.
            myd = cheb(nx, ny, ox, oy)
            score = -myd * 10 - abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2)

        # Mild preference to avoid stepping away from the already best target area (stable tie-break).
        # Deterministic tie-break: prefer smaller dx, then smaller dy.
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    return [int(best[1]), int(best[2])]