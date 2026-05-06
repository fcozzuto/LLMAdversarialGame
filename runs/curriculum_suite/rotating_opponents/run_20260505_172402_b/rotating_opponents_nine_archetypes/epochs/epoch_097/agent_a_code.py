def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    if not valid(sx, sy):
        for yy in range(h):
            for xx in range(w):
                if valid(xx, yy):
                    sx, sy = xx, yy
                    break
            if valid(sx, sy):
                break

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    center = (w / 2.0 - 0.5, h / 2.0 - 0.5)

    best = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        me = (nx, ny)
        opp = (ox, oy)
        # nearest resource heuristic
        if resources:
            mind = 10**9
            for r in resources:
                if r == me:
                    mind = 0
                    break
                d = dist(me, r)
                if d < mind:
                    mind = d
        else:
            mind = abs(me[0] - center[0]) + abs(me[1] - center[1])

        # prefer collecting soon, keep some separation, avoid walking into opponent control
        d_opp = dist(me, opp)
        score = -mind + 0.06 * d_opp

        if best_score is None or score > best_score:
            best_score = score
            best = [dx, dy]
        elif score == best_score:
            # deterministic tie-break: prefer staying, then lower |dx|, then lower |dy|
            if (best[0] != dx or best[1] != dy):
                if (dx, dy) == (0, 0):
                    best = [dx, dy]
                elif abs(dx) < abs(best[0]) or (abs(dx) == abs(best[0]) and abs(dy) < abs(best[1])):
                    best = [dx, dy]

    return best