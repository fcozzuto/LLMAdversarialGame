def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if (0, 0) not in deltas:
        deltas.append((0, 0))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obst_pen(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx or dy:
                    if (x + dx, y + dy) in obstacles:
                        c += 1
        return c

    def best_target_for(posx, posy):
        best = None
        bestv = -10**9
        for rx, ry in resources:
            d = cheb(posx, posy, rx, ry)
            if d == 0:
                return (rx, ry, d)
            od = cheb(ox, oy, rx, ry)
            # Prefer targets where we're not far behind opponent; otherwise reduce weight.
            lead = od - d  # positive => we are closer/equal
            # Also mildly prefer resources with fewer nearby obstacles to route reliably.
            ob = obst_pen(rx, ry)
            v = (lead * 3.0) - d - ob * 0.6
            if v > bestv:
                bestv = v
                best = (rx, ry, d)
        return best

    target = best_target_for(sx, sy)
    if not target:
        return [0, 0]
    tx, ty, _ = target

    # If opponent is adjacent to our target, try to shift to an alternative target deterministically.
    if cheb(ox, oy, tx, ty) <= 1:
        target2 = None
        bestv2 = -10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            d = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            lead = od - d
            ob = obst_pen(rx, ry)
            v = (lead * 3.0) - d - ob * 0.6
            if v > bestv2:
                bestv2 = v
                target2 = (rx, ry)
        if target2:
            tx, ty = target2

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(nx, ny, ox, oy)

        # Encourage capture, avoid being too close to opponent when it benefits them.
        capture = 1000.0 if myd == 0 else 0.0
        step_to_target = -myd * 6.0
        avoid_opp = -max(0, 2 - oppd) * 18.0  # strong if within 1-2
        # Also keep away from obstacles a bit.
        risk = obst_pen(nx, ny) * 2.5

        # If opponent is closer to target than we are in the resulting position, discourage.
        my_to = cheb(nx, ny, tx, ty)
        opp_to = cheb(ox, oy, tx, ty)
        if opp_to <