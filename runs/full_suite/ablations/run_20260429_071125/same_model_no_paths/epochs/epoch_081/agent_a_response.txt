def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Consider only the most relevant nearby targets for a materially different policy
    resources.sort(key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    top = resources[:min(6, len(resources))]

    best_mv = (0, 0)
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue

            on_res = (nx, ny) in set(top)  # cheap local set behavior
            my_d0 = 0 if on_res else None

            # Evaluate move by the best "advantage" target it enables next
            best_adv = None
            best_my_dist = None
            for rx, ry in top:
                my_d = 0 if (nx, ny) == (rx, ry) else cheb(nx, ny, rx, ry)
                op_d = cheb(ox, oy, rx, ry)
                adv = op_d - my_d
                key2 = (adv, -my_d, -rx, -ry)
                if best_adv is None or key2 > (best_adv, best_my_dist, 0, 0):
                    best_adv = adv
                    best_my_dist = my_d

            # Primary: maximize advantage (opp sooner/later). Secondary: minimize my distance.
            # Tertiary: prefer moves that head toward the global nearby cluster center (deterministic).
            cx = sum(x for x, _ in top) // len(top)
            cy = sum(y for _, y in top) // len(top)
            head = -cheb(nx, ny, cx, cy)

            key = (best_adv, -(best_my_dist if best_my_dist is not None else 0), head, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]