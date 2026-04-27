def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obst = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obst.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obst:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not inb(sx, sy):
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose target: prioritize resources where we have an advantage in distance vs opponent.
    tx, ty = None, None
    if resources:
        best = None
        for x, y in resources:
            ds = cheb(sx, sy, x, y)
            do = cheb(ox, oy, x, y)
            score = (do - ds, -ds, -(abs(x - (w - 1) // 2) + abs(y - (h - 1) // 2)), x, y)
            if best is None or score > best:
                best = score
                tx, ty = x, y

    # If no resources, drift toward center but keep away from opponent a bit.
    if tx is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_m, best_s = (0, 0), None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obst:
                continue
            ns = cheb(nx, ny, cx, cy) - 0.25 * cheb(nx, ny, ox, oy) + 0.01 * (dx * dx + dy * dy)
            s = (-ns, dx, dy)
            if best_s is None or s > best_s:
                best_s = s
                best_m = (dx, dy)
        return [best_m[0], best_m[1]]

    # Move one step toward target, but only if not blocked; otherwise choose best alternative.
    desired = (0, 0)
    if tx > sx: desired = (1, desired[1])
    elif tx < sx: desired = (-1, desired[1])
    if ty > sy: desired = (desired[0], 1)
    elif ty < sy: desired = (desired[0], -1)

    best_m, best_val = (0, 0), None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        ns = cheb(nx, ny, tx, ty)
        no = cheb(nx, ny, ox, oy)
        adv = (cheb(nx, ny, tx, ty) - cheb(ox, oy, tx, ty))
        tie = (abs(dx - desired[0]) + abs(dy - desired[1]), dx, dy)
        val = (-ns, adv, no * 0.01, -tie[0], -tie[1], -tie[2])
        if best_val is None or val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]