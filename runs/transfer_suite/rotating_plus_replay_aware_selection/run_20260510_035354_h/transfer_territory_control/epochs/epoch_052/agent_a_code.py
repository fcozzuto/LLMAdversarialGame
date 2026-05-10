def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    unclaimed = observation.get("unclaimed_cells") or []
    self_terr = observation.get("self_territory") or []
    opp_terr = observation.get("opponent_territory") or []
    obstacles = observation.get("obstacles") or []

    uset = {(c[0], c[1]) for c in unclaimed if isinstance(c, (list, tuple)) and len(c) >= 2}
    sset = {(c[0], c[1]) for c in self_terr if isinstance(c, (list, tuple)) and len(c) >= 2}
    oset = {(c[0], c[1]) for c in opp_terr if isinstance(c, (list, tuple)) and len(c) >= 2}
    obs = {(c[0], c[1]) for c in obstacles if isinstance(c, (list, tuple)) and len(c) >= 2}

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

    targets = list(uset) if uset else list(oset) if oset else [(ox, oy)]
    opp_targets = list(oset) if oset else [(ox, oy)]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        val = 0
        if (nx, ny) in oset:
            val += 8
        elif (nx, ny) in uset:
            val += 6
        elif (nx, ny) in sset:
            val += 2
        else:
            val += 1

        if targets:
            d = 10**9
            for tx, ty in targets:
                dd = man(nx, ny, tx, ty)
                if dd < d:
                    d = dd
            val += 10 - min(10, d)
        if opp_targets:
            do = 10**9
            for tx, ty in opp_targets:
                dd = man(nx, ny, tx, ty)
                if dd < do:
                    do = dd
            val += min(6, 6 - do)  # closer to opponent territory is better

        # discourage bumping into opponent territory only through long detours
        val += (-1 if (nx, ny) in sset and man(nx, ny, ox, oy) > man(ax, ay, ox, oy) else 0)

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]