def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def obstacle_pressure(x, y):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                px, py = x + dx, y + dy
                if (px, py) in obstacles:
                    c += 1
        return c

    # Choose a target deterministically: closest by Chebyshev, tie by x then y
    target = None
    bestd = 10**9
    for rx, ry in resources:
        d = cheb(sx, sy, rx, ry)
        if d < bestd or (d == bestd and (rx, ry) < target):
            bestd = d
            target = (rx, ry)
    tx, ty = target

    my_dist_now = cheb(sx, sy, tx, ty)
    op_dist_now = cheb(ox, oy, tx, ty)

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my_d = cheb(nx, ny, tx, ty)
        op_d = cheb(ox + 0, oy + 0, tx, ty)  # static opponent distance baseline
        # Approx: encourage moves that reduce my distance and make opponent less able to intercept by considering my gain vs my drop relative to opponent
        # Also slightly prefer moving away from opponent when equal progress is possible
        away = cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy)
        res_spread = 0
        for (rx, ry) in resources:
            res_spread += 1 if cheb(nx, ny, rx, ry) > my_d else 0
        press = obstacle_pressure(nx, ny)

        val = (-my_d * 10.0) + (-press * 1.5) + (away * 0.7) + (res_spread * 0.05)
        # Blocking term: if I move closer, ensure opponent isn't already extremely close; deterministically penalize when opponent is closer than me to target
        if op_dist_now <= my_dist_now:
            val -= (my_d * 0.8)
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]