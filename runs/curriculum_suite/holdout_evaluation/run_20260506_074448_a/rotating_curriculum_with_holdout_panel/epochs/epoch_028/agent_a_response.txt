def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def best_resource_dist(x, y):
        if not resources:
            return 0
        md = 10**9
        for rx, ry in resources:
            d = man(x, y, rx, ry)
            if d < md:
                md = d
        return md

    def mobility(x, y):
        cnt = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                cnt += 1
        return cnt

    # Evaluate moves with a deterministic tradeoff:
    # 1) closest to resources
    # 2) maximize distance from opponent (avoid entanglement)
    # 3) maximize mobility (avoid traps)
    # 4) minimize step cost
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        rd = best_resource_dist(nx, ny)
        od = man(nx, ny, ox, oy)
        mob = mobility(nx, ny)
        cost = abs(dx) + abs(dy)
        cand = (rd, -od, -mob, cost, dx, dy)
        if best is None or cand < best:
            best = cand

    if best is not None:
        return [best[4], best[5]]

    return [0, 0]