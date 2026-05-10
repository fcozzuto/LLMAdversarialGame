def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    oset = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    self_terr = observation.get("self_territory") or []
    uset = {(p[0], p[1]) for p in self_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    opp_terr = observation.get("opponent_territory") or []
    pset = {(p[0], p[1]) for p in opp_terr if isinstance(p, (list, tuple)) and len(p) >= 2}

    unclaimed = observation.get("unclaimed_cells") or []
    cset = {(p[0], p[1]) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2}

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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Frontier bias: unclaimed cells adjacent to our territory
    frontier = []
    if uset and cset:
        for (x, y) in cset:
            if any((x + dx, y + dy) in uset for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]):
                frontier.append((x, y))
    targets = frontier if frontier else (list(cset) if cset else (list(pset) if pset else [(ox, oy)]))

    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        # Immediate benefit
        if (nx, ny) in cset:
            v = 1000
        elif (nx, ny) in pset:
            v = 250
        else:
            v = 0

        # Future: aim for a good target, while staying away from opponent
        # Use best among targets without full search: compute nearest score proxy.
        min_proxy = 10**9
        for tx, ty in targets:
            d = man(nx, ny, tx, ty)
            # Prefer cells that are far from opponent (reduce immediate contests)
            dist_opp = man(nx, ny, ox, oy)
            proxy = d - 0.15 * dist_opp
            if proxy < min_proxy:
                min_proxy = proxy

        # Also discourage moving closer to opponent when not taking unclaimed
        opp_close_pen = 0
        if (nx, ny) not in cset and man(nx, ny, ox, oy) <= man(ax, ay, ox, oy):
            opp_close_pen = 30

        v = v - min_proxy - opp_close_pen
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]