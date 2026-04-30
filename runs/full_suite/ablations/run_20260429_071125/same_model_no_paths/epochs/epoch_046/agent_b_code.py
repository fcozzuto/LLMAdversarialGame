def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = (0, 0)
    best_val = -10**18

    # Deterministic tie-breaking via move order.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # If resources exist, prefer taking ones opponent is less likely to reach.
        if resources:
            total = -0.05 * cheb(nx, ny, ox, oy)  # keep some pressure
            for rx, ry in resources:
                d_self = man((nx, ny), (rx, ry))
                d_opp = man((ox, oy), (rx, ry))
                # Want resources where we gain relative proximity; also prefer immediate closeness.
                gain = d_opp - d_self
                # Strongly prefer picking nearer targets; discourage unreachable/slow ones.
                val = 3.0 * gain - 0.8 * d_self
                if (rx, ry) in blocked:
                    val -= 1000
                total += val / (1 + len(resources))
            score = total
        else:
            # No resources: move to reduce distance to opponent's likely path area.
            score = -cheb(nx, ny, ox, oy)

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]