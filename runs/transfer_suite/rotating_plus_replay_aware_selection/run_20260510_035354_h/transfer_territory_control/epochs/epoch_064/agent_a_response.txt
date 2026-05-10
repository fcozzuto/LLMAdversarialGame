def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    unclaimed = observation.get("unclaimed_cells") or []
    uset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

    self_terr = observation.get("self_territory") or []
    sset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    opp_terr = observation.get("opponent_territory") or []
    opset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    bestv = -10**18

    # Frontier targets: our territory cells adjacent to unclaimed.
    frontier = set()
    if sset and uset:
        for (x, y) in sset:
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in uset:
                    frontier.add((nx, ny))
    targets = frontier if frontier else (uset if uset else (opset if opset else {(ox, oy)}))

    centerx, centery = (w - 1) / 2.0, (h - 1) / 2.0
    for dx, dy in dirs:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        v = 0
        if (nx, ny) in uset:
            v += 7
        elif (nx, ny) in opset:
            v += 5
        elif (nx, ny) in sset:
            v += 1

        d_to_opp = man(nx, ny, ox, oy)
        v += -0.12 * d_to_opp  # generally keep distance unless capturing

        d_t = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            if d < d_t:
                d_t = d
        v += -0.55 * d_t  # move toward best frontier/unclaimed

        # Slight center preference to avoid getting trapped on edges.
        v += -0.02 * (abs(nx - centerx) + abs(ny - centery))

        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]