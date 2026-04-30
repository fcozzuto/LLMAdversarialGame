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
        tx, ty = W // 2, H // 2
        if (tx, ty) in obs or not (0 <= tx < W and 0 <= ty < H):
            tx, ty = 0, 0 if (0, 0) not in obs else (W - 1, H - 1)
        resources = [(tx, ty)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # Precompute opponent best distances to all resources (from current position)
    res_info = []
    for rx, ry in resources:
        res_info.append((rx, ry, man(ox, oy, rx, ry)))

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Score: prioritize moves that (1) reduce our distance, and (2) deny by being no worse than opponent.
        self_best = 10**9
        deny_gap_best = -10**9
        for rx, ry, od in res_info:
            sd = man(nx, ny, rx, ry)
            if sd < self_best:
                self_best = sd
            gap = od - sd  # positive means we are closer than opponent
            if sd <= od and gap > deny_gap_best:
                deny_gap_best = gap

        # If we can't be closer to any resource, still move toward the closest one.
        if deny_gap_best < -10**8:
            deny_gap_best = -self_best  # mild penalty for not contesting

        # Encourage slight movement toward center to avoid corner stagnation when tied
        cx, cy = (W - 1) / 2.0, (H - 1) / 2.0
        center_boost = -abs((nx - cx)) - abs((ny - cy))

        val = (-self_best * 10) + (deny_gap_best * 6) + center_boost
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]