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
        tx, ty = (W - 1) // 2, (H - 1) // 2
        if (tx, ty) in obs:
            tx, ty = sx, sy
        resources = [(tx, ty)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Prefer states where we are much closer than opponent, and closer overall.
        # Also slightly prefer moving toward the closest resource we are not currently behind on.
        min_self = 10**9
        max_adv = -10**9
        tie_break = 0
        for rx, ry in resources:
            ds = man(nx, ny, rx, ry)
            do = man(ox, oy, rx, ry)
            adv = do - ds  # positive is good
            if ds < min_self:
                min_self = ds
                tie_break = rx + 10 * ry
            if adv > max_adv:
                max_adv = adv

        # Strongly encourage denying if opponent is closer to any resource.
        val = 100 * max_adv - 3 * min_self + (-(tie_break) * 0.001)
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]