def choose_move(observation):
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    blocked = set()
    for b in obstacles:
        try:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))
        except:
            pass

    res = []
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res.append((rx, ry))
        except:
            pass

    if not res:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    ox, oy = int(op[0]), int(op[1])

    best_delta = [0, 0]
    best_val = -10**9

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # immediate capture if stepping onto a resource
        step_capture = 0
        for rx, ry in res:
            if rx == nx and ry == ny:
                step_capture = 1
                break

        # Choose a target resource maximizing advantage after this move
        # Advantage: (opp distance - my distance). Larger is better.
        best_adv = -10**9
        for rx, ry in res:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            adv = od - md
            # small bias to earlier approach and relative positioning
            bias = (od - md)
            if adv > best_adv:
                best_adv = adv
        # Prefer capturing or safer advantage; add tiny preference for moving forward toward chosen advantage
        val = best_adv + (2 * step_capture)
        if val > best_val:
            best_val = val
            best_delta = [dx, dy]

    return best_delta if best_delta in ([d[0], d[1]] for d in deltas) else [0, 0]