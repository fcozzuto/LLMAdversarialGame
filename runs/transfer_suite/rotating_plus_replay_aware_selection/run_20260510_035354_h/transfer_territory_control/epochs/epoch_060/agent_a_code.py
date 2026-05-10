def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    unclaimed = observation.get("unclaimed_cells") or []
    obstacles = observation.get("obstacles") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []

    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}
    sset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}
    pset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        d1 = x1 - x2
        if d1 < 0: d1 = -d1
        d2 = y1 - y2
        if d2 < 0: d2 = -d2
        return d1 + d2

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    # Frontier targets: cells adjacent to our territory (prefer unclaimed), else chase closest unclaimed/opp
    frontier = []
    for (x, y) in sset:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in sset and (nx, ny) not in oset:
                    frontier.append((nx, ny))
    t_unclaimed = [c for c in frontier if c in uset]
    target_list = t_unclaimed if t_unclaimed else (list(uset) if uset else list(pset) if pset else [(ox, oy)])

    # Deterministic tie-breaker order: fixed move order already
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue

        v = 0
        # Immediate cell value
        if (nx, ny) in uset:
            v += 30
        if (nx, ny) in pset:
            v += 18  # flipping on entry
        if (nx, ny) in sset:
            v += 6

        # Reduce distance to best strategic target
        dmin = 10**9
        for tx, ty in target_list:
            d = man(nx, ny, tx, ty)
            if d < dmin:
                dmin = d
        v += (20 - min(20, dmin))

        # Prefer moves that increase "access": how many neighboring unclaimed/opp cells we can take next
        neigh = 0
        for adx in (-1, 0, 1):
            for ady in (-1, 0, 1):
                if adx == 0 and ady == 0:
                    continue
                ex, ey = nx + adx, ny + ady
                if inb(ex, ey) and (ex, ey) not in oset and ((ex, ey) in uset or (ex, ey) in pset):
                    neigh += 1
        v += neigh * 2

        # Mild anti-stall: discourage staying unless it is best by value
        if dx == 0 and dy == 0:
            v -= 1

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]