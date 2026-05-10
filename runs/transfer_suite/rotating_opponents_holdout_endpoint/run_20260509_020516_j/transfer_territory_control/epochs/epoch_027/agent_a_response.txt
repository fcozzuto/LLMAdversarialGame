def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (W - 1, H - 1))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    unclaimed = []
    for p in observation.get("unclaimed_cells") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                unclaimed.append((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))

    targets = unclaimed if unclaimed else resources if resources else [(ox, oy)]
    best = None
    best_val = -10**18

    # Prefer cells near the "battle line" and where we can arrive much sooner than opponent.
    # Also slightly prefer cells closer to center to avoid getting boxed.
    cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
    for x, y in targets:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        if ds == 0:
            val = 10**9
        else:
            line = abs((x - (W - 1 - ox)) - (sx - (W - 1 - x))) + abs((y - (H - 1 - oy)) - (sy - (H - 1 - y)))
            # ds small, do large is good; resources get a bigger weight (in case unclaimed empty).
            res_bonus = 2.5 if (x, y) in set(resources) and (x, y) in targets else 0.0
            center = abs(x - cx) + abs(y - cy)
            val = (do - ds) * 4.0 - ds * 0.2 + line * 0.02 - center * 0.01 + res_bonus
        if val > best_val:
            best_val = val
            best = (x, y)

    tx, ty = best if best is not None else (sx, sy)

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Obstacle-safe nudge: try among 5 deterministic moves that reduce manhattan to target.
    moves = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (0, 0)]
    bestm = (0, 0)
    bestd = 10**9
    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        if d < bestd:
            bestd = d
            bestm = (mdx, mdy)
    return [int(bestm[0]), int(bestm[1])]