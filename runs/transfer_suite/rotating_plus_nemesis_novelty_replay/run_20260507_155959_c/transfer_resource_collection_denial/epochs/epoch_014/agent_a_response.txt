def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles if p is not None}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        ax = x1 - x2
        ay = y1 - y2
        return (ax if ax >= 0 else -ax) + (ay if ay >= 0 else -ay)

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    res = [(r[0], r[1]) for r in resources if r is not None and (r[0], r[1]) not in blocked]
    if not res:
        return [0, 0]

    # Can opponent grab a resource next turn? (one-step reach)
    opp_reach1 = set()
    for rx, ry in res:
        if md(ox, oy, rx, ry) <= 1:
            # ensure at least one obstacle-free neighbor to that cell exists (approx via distance check)
            opp_reach1.add((rx, ry))

    best = None
    bestv = -10**18
    # Deterministic tie-break ordering
    legal.sort(key=lambda t: (t[0], t[1]))
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = 0

        # Immediate pickup
        for rx, ry in res:
            if rx == nx and ry == ny:
                v += 100000

        # Advantage: how much closer we are than opponent, aggregated
        for rx, ry in res:
            d_self = md(nx, ny, rx, ry)
            d_op = md(ox, oy, rx, ry)
            adv = d_op - d_self
            v += 180 * adv  # prioritizes being closer than opponent

            # If opponent can grab it next turn, we strongly prefer moving there or closer-than-them
            if (rx, ry) in opp_reach1:
                if d_self == 0:
                    v += 80000
                elif d_self <= 1 and d_op > 1:
                    v += 12000
                else:
                    v -= 2500

        # Secondary: move toward the best remaining resource (min our distance with opponent safety)
        min_d = 10**9
        for rx, ry in res:
            min_d = d if (d := md(nx, ny, rx, ry)) < min_d else min_d
        v -= 2 * min_d

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]