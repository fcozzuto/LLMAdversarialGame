def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    sx, sy = int(sx), int(sy)

    blocks = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocks.add((x, y))

    self_terr = set((int(x), int(y)) for x, y in (observation.get("self_territory") or []))
    opp_terr = set((int(x), int(y)) for x, y in (observation.get("opponent_territory") or []))
    unclaimed = set((int(x), int(y)) for x, y in (observation.get("unclaimed_cells") or []))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocks

    def d2(x, y, tx, ty):
        dx, dy = x - tx, y - ty
        return dx * dx + dy * dy

    # Choose next cell that (1) pressures opponent boundary, else (2) expands into unclaimed,
    # with a mild preference for staying away from corners unless it advances.
    best = None
    best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        val = 0
        if (nx, ny) in opp_terr:
            val += 220  # flipping on entry to opponent control
        elif (nx, ny) in unclaimed:
            val += 55   # new territory claim

        # Frontier pressure: move to/near opponent territory.
        if opp_terr:
            min_opp = 10**9
            for ox, oy in opp_terr:
                dd = d2(nx, ny, ox, oy)
                if dd < min_opp:
                    min_opp = dd
            val += 120 - (min_opp ** 0.5) * 8  # closer is better

            # Stronger preference if adjacent to opponent territory (likely to cause flips next).
            adj = False
            for ax, ay in dirs:
                xx, yy = nx + ax, ny + ay
                if ok(xx, yy) and (xx, yy) in opp_terr:
                    adj = True
                    break
            if adj:
                val += 60
        else:
            # No opponent territory visible: expand systematically toward nearest unclaimed.
            if unclaimed:
                min_u = 10**9
                for ux, uy in unclaimed:
                    dd = d2(nx, ny, ux, uy)
                    if dd < min_u:
                        min_u = dd
                val += 70 - (min_u ** 0.5) * 10

        # Avoid dead-ends: prefer moves that have at least one free neighbor.
        free_neighbors = 0
        for ax, ay in dirs:
            xx, yy = nx + ax, ny + ay
            if ok(xx, yy):
                free_neighbors += 1
        val += free_neighbors * 2

        # Mild corner/edge discipline: prefer not to cling to edges unless targeting.
        edge = nx in (0, w - 1) or ny in (0, h - 1)
        if edge and not opp_terr:
            val -= 5

        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]