def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inside(px, py):
                blocked.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def md(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    best = None
    best_key = None
    for cx, cy in resources:
        sd = md(sx, sy, cx, cy)
        od = md(ox, oy, cx, cy)
        if sd < od:
            key = (2, od - sd, -sd, -cx, -cy)
        else:
            key = (1, -(od - sd), -sd, -cx, -cy)
        if best_key is None or key > best_key:
            best_key = key
            best = (cx, cy)

    tx, ty = best

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and (nx, ny) not in blocked:
                moves.append((dx, dy))

    if not moves:
        return [0, 0]

    best_move = None
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        sd1 = md(nx, ny, tx, ty)
        od1 = md(ox, oy, tx, ty)
        adv_flag = 1 if sd1 < od1 else 0
        key = (adv_flag, od1 - sd1, -sd1, -dx, -dy)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]