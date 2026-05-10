def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [7, 7])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    selfT = set()
    for p in observation.get("self_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            selfT.add((int(p[0]), int(p[1])))

    opT = set()
    for p in observation.get("opponent_territory") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            opT.add((int(p[0]), int(p[1])))

    unT = set()
    for p in observation.get("unclaimed_cells") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            unT.add((int(p[0]), int(p[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def adj_count(x, y, S):
        c = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in S:
                    c += 1
        return c

    def best_neighbor_dist(x, y, S):
        if not S:
            return 999
        bd = 999
        for (px, py) in S:
            d = abs(px - x) + abs(py - y)
            if d < bd:
                bd = d
        return bd

    # Determine target behavior: expand to unclaimed near our frontier; avoid stepping into opponent blobs unless it opens capture.
    best_mv = (0, 0)
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        t_sc = 0
        if (nx, ny) in selfT:
            t_sc += 25
        elif (nx, ny) in unT:
            t_sc += 60 + 10 * adj_count(nx, ny, selfT)
        elif (nx, ny) in opT:
            # flipping on entry is enabled; only take if it seems like an edge and not deep inside opponent control
            t_sc += 70 + 12 * adj_count(nx, ny, selfT) - 10 * adj_count(nx, ny, opT)
            # also prefer moves that reduce distance to opponent front rather than chasing blindly
            t_sc += -2 * best_neighbor_dist(nx, ny, opT) + 3 * best_neighbor_dist(nx, ny, unT)
        else:
            # possibly outside listed sets due to timing; treat as low but allow if it reduces opponent distance
            t_sc += 5

        # Frontier shaping: prefer cells adjacent to unclaimed and not adjacent-heavy to opponent territory
        t_sc += 6 * adj_count(nx, ny, unT) - 4 * adj_count(nx, ny, opT)

        # Keep away from opponent if equally good
        d_op = abs(nx - ox) + abs(ny - oy)
        t_sc += -0.5 * d_op

        # Deterministic tie-break: lexicographic over (dx,dy)
        if t_sc > best_sc or (t_sc == best_sc and (dx, dy) < best_mv):
            best_sc = t_sc
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]