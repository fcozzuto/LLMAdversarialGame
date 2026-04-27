def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not inb(sx, sy):
        return [0, 0]

    # Pick resource where we are most ahead vs opponent (largest opp_dist - my_dist), tie-break by my_dist then coords.
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            md = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            lead = od - md
            key = (-lead, md, rx, ry)  # minimize key == maximize lead
            if best is None or key < best:
                best = key
                target = (rx, ry)
    # If no resources (shouldn't happen often), just drift toward center.
    if target is None:
        cx, cy = w // 2, h // 2
        target = (cx, cy)

    tx, ty = target
    # Choose move greedily toward target, but also prefer moves that keep us closer than opponent to that target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)  # opponent distance unchanged this move; use to favor "tempo advantage"
        val = (myd, -opd, abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]