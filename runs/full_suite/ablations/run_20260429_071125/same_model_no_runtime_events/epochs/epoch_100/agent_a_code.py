def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    # Pick target that we can reach earlier than opponent; tie-break by closer to us.
    target = None
    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prioritize positive advantage, then minimal self distance, then deterministic coordinate
        adv = od - sd
        score = (adv, -sd, -rx, -ry)
        if best is None or score > best:
            best = score
            target = (rx, ry)

    if target is None:
        # No resources: drift to center-ish while avoiding obstacles, deterministic.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = (-cheb(nx, ny, cx, cy), -dx, -dy)
            if best_val is None or val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = target

    # Choose move that reduces distance to target; if blocked, pick best alternative.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = cheb(nx, ny, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer faster approach and also prevent opponent from gaining advantage
        key = (od - sd, -sd, -abs(nx - ox) - abs(ny - oy), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]