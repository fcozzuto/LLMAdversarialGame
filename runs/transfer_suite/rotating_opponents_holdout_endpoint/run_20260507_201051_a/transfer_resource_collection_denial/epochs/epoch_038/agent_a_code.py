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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def best_resource_from(x, y):
        if not resources:
            return None
        best = None
        bestv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = abs(rx - x) + abs(ry - y)
            do = abs(rx - ox) + abs(ry - oy)
            v = (do - ds) * 10 - ds * 2
            # small deterministic tie-breaker: prefer nearer to center
            v -= abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2) * 0.01
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    def cell_blocked(nx, ny):
        return (nx, ny) in obstacles

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or cell_blocked(nx, ny):
            continue
        target = best_resource_from(nx, ny)
        if target is None:
            # no resources: go closer to opponent deterministically
            val = - (abs(nx - ox) + abs(ny - oy)) * 3 + (dx == 0 and dy == 0) * -5
        else:
            rx, ry = target
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            val = (do - ds) * 10 - ds * 2 - (abs(nx - ox) + abs(ny - oy)) * 0.2
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    # If everything is blocked, stay put.
    dx, dy = best_move
    if not (dx in (-1, 0, 1) and dy in (-1, 0, 1)):
        return [0, 0]
    return [int(dx), int(dy)]