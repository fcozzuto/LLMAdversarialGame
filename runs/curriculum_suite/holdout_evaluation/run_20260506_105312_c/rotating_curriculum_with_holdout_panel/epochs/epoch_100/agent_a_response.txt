def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mdist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def edge_pen(x, y):
        return 2.0 if x in (0, w - 1) or y in (0, h - 1) else 0.0

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = None
        bestv = -1e18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            v = mdist(nx, ny, ox, oy) - 0.5 * edge_pen(nx, ny)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best is not None else [0, 0]

    # Choose target deterministically: prefer interior/safer resources, but still close.
    target = None
    targetv = -1e18
    for x, y in resources:
        d1 = mdist(sx, sy, x, y)
        d2 = mdist(ox, oy, x, y)
        v = (-1.8 * d1) + (0.9 * d2) - edge_pen(x, y) + (0.05 * (x + y))
        if v > targetv or (v == targetv and (x, y) < (target[0], target[1]) if target else True):
            targetv = v
            target = (x, y)

    tx, ty = target

    # Move one step toward target; among legal moves pick best resulting position value.
    best = (0, 0)
    bestv = -1e18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        v = (-2.2 * mdist(nx, ny, tx, ty)) + (0.8 * mdist(nx, ny, ox, oy)) - 0.6 * edge_pen(nx, ny) + (0.01 * (nx + ny))
        if v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]