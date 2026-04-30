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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not inb(sx, sy):
        for dx, dy in dirs:
            if inb(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        for tx, ty in resources:
            ds = dist(sx, sy, tx, ty)
            do = dist(ox, oy, tx, ty)
            # Prefer targets opponent can't reach as quickly; then minimize our distance
            key = (do - ds, -ds, tx, ty)
            if best is None or key > best[0]:
                best = (key, tx, ty)
        _, tx, ty = best
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        cand = (sx + dx, sy + dy)
        if inb(*cand):
            return [dx, dy]

        # If direct step is blocked, pick best alternative deterministically by ds then tie by direction order
        best_step = None
        for ddx, ddy in dirs:
            nx, ny = sx + ddx, sy + ddy
            if not inb(nx, ny):
                continue
            nds = dist(nx, ny, tx, ty)
            key = (0 if (nx == sx and ny == sy) else 1, -nds, -abs(tx - nx) - abs(ty - ny), ddx, ddy)
            if best_step is None or key > best_step[0]:
                best_step = (key, [ddx, ddy])
        return best_step[1] if best_step else [0, 0]

    # No resources: move toward center while avoiding obstacles
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    tx, ty = int(cx), int(cy)
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)
    if inb(sx + dx, sy + dy):
        return [dx, dy]
    for ddx, ddy in dirs:
        if inb(sx + ddx, sy + ddy):
            return [ddx, ddy]
    return [0, 0]