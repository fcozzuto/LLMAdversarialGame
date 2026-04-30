def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dirs = moves

    best = None
    best_score = -10**18

    ox = int((observation.get("opponent_position") or [w - 1, h - 1])[0])
    oy = int((observation.get("opponent_position") or [w - 1, h - 1])[1])

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        # Prefer moves that approach the closest resource; if none, approach opponent.
        if resources:
            dmin = 10**9
            for rx, ry in resources:
                ddx = rx - nx
                if ddx < 0: ddx = -ddx
                ddy = ry - ny
                if ddy < 0: ddy = -ddy
                d = ddx if ddx > ddy else ddy
                if d < dmin: dmin = d
        else:
            ddx = ox - nx
            if ddx < 0: ddx = -ddx
            ddy = oy - ny
            if ddy < 0: ddy = -ddy
            dmin = ddx if ddx > ddy else ddy

        # Avoid tight spots: count free neighbors (including staying).
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                free += 1

        # Deterministic tie-break by lexicographic move preference.
        score = (-dmin * 1000) + free

        if best is None or score > best_score:
            best_score = score
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best