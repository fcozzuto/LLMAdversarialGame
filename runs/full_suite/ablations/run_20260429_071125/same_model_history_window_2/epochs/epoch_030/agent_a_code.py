def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def kd(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance for diagonal movement

    if not resources:
        best = (0, 0, -10**18)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = kd(nx, ny, ox, oy) - (1 if (nx, ny) == (sx, sy) else 0)
            if val > best[2]:
                best = (dx, dy, val)
        return [best[0], best[1]]

    # Choose the resource where we have the best race advantage; tie-break by nearer self.
    target = resources[0]
    best_adv = -10**18
    best_self_d = 10**18
    for rx, ry in resources:
        ds = kd(sx, sy, rx, ry)
        do = kd(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        if adv > best_adv or (adv == best_adv and ds < best_self_d):
            best_adv = adv
            best_self_d = ds
            target = (rx, ry)

    rx, ry = target

    # Move towards target while respecting obstacles; add opponent pressure if they are closer to the target.
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        ds2 = kd(nx, ny, rx, ry)
        do2 = kd(ox, oy, rx, ry)
        cur_ds = kd(sx, sy, rx, ry)
        improved = (cur_ds - ds2)
        adv_now = do2 - ds2
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        # Encourage not getting stuck and better winning odds.
        val = (2.5 * adv_now) + (1.2 * improved) - (0.4 * stay_pen) - (0.01 * ds2)
        if val > best[2]:
            best = (dx, dy, val)

    return [int(best[0]), int(best[1])]