def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if ok(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If resources exist: maximize "can I beat opponent to a resource?"
    if resources:
        best_mv = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            # Small tie-break: prefer staying away from opponent unless it helps win.
            for rx, ry in resources:
                ds = dist_cheb(nx, ny, rx, ry)
                do = dist_cheb(ox, oy, rx, ry)
                # Positive means opponent is further (or you are closer by enough margin).
                val = (do - ds) * 1000
                # If opponent is very close, prefer moves that increase their distance more.
                val += (dist_cheb(ox, oy, nx, ny) - dist_cheb(nx, ny, rx, ry))
                # Prefer closer-to-resource paths when margins equal.
                val -= ds
                if val > best_val:
                    best_val = val
                    best_mv = (dx, dy)
        return [int(best_mv[0]), int(best_mv[1])]

    # No resources: drift toward center while keeping distance from opponent.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_mv = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        dc = abs(nx - cx) + abs(ny - cy)
        dpo = dist_cheb(nx, ny, ox, oy)
        val = -dc * 10 + dpo
        if val > best_val:
            best_val = val
            best_mv = (dx, dy)
    return [int(best_mv[0]), int(best_mv[1])]