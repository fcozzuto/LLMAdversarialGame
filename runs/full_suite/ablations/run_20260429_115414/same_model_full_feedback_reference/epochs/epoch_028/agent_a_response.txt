def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                resources.append((x, y))
    if not resources:
        resources = [((W - 1) // 2, (H - 1) // 2)]
        if resources[0] in obs:
            resources = [(0, 0)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    # Pick the "best" resource by potential control: we want to be closer than opponent.
    resources_sorted = sorted(resources, key=lambda r: (-(man(ox, oy, r[0], r[1]) - man(sx, sy, r[0], r[1])), r[0], r[1]))
    target = resources_sorted[0]

    best = (0, 0)
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        myd = man(nx, ny, target[0], target[1])
        opd = man(ox, oy, target[0], target[1])

        # Value: reduce my distance while keeping/expanding opponent disadvantage.
        val = (opd - myd, -myd, -abs(nx - ox) - abs(ny - oy), dx == 0 and dy == 0)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]